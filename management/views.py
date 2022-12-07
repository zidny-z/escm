# from decimal import Decimal
# from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.shortcuts import get_object_or_404
# from django.utils.datastructures import MultiValueDictKeyError

# from somewhere import handle_uploaded_file 
import time

from .models import *
from .forms import *
from django.db.models import F, Q

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/dashboard/')
    else: 
        return render(request, "index.html")

def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/dashboard/')
    else: 
        if request.method == 'POST':
            # Attempt to sign user in
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)

            # Check if authentication successful
            if user is not None:
                auth_login(request, user)
                return HttpResponseRedirect(reverse('dashboard'))
                # return render('dashboard')
                # return HttpResponse('Authenticated successfully')
                    
            else:
                # return HttpResponse('Authenticated disabled')
                # print(username,password)
                return render(request, 'login.html', {
                    'message': 'Invalid username and/or password.',
                    'title': 'Login',
                })
        else:
            return render(request, 'login.html', {
                'title': 'Login',
            })

@login_required
def dashboard(request):
    currentYear= timezone.now().year
    currentDay= timezone.now().day
    if request.user.role == "SV": 
        return render(request, "dashboardSV.html",{
            'bengkel_count': Bengkel.objects.count(),
            'supplier_count': Supplier.objects.count(),
            'product_count': Product.objects.count(),
            'need_stock': Stock.objects.filter(stockCount__lt=F('minStock')).count(),
            # 'transaksi_sebulan': Order.objects.filter(orderDate__year=currentYear, orderDate__month=11).count(),
            'transaksi_setahun': Order.objects.filter(orderDate__year=currentYear).count(),
            'penawaran_today': Penawaran.objects.filter(tawarDate__day=currentDay).count(),
            'produk_tambahan_today': Product.objects.filter(addDate__day=currentDay).count(),
        })
    elif request.user.role == "LB":
        my_id = request.user.id
        bengkel_id = Bengkel.objects.select_related('owner').get(owner_id=my_id)
        return render(request, "dashboardLB.html",{
            'my_id': my_id,
            'bengkel_id': bengkel_id.id,
            'category': Category.objects.prefetch_related('product','product__stock').filter(product__stock__bengkel=bengkel_id).count(),
            'supplier_count': Supplier.objects.count(),
            'product_count': Stock.objects.filter(bengkel=bengkel_id).count(),
            'need_stock': Stock.objects.filter(bengkel=bengkel_id ,stockCount__lt=F('minStock')).count(),
            'transaksi_setahun': Order.objects.filter(orderDate__year=currentYear, bengkel=bengkel_id).count(),
            'penawaran_today': Penawaran.objects.filter(tawarDate__day=currentDay, tujuan=my_id).count(),
            'produk_tambahan_today': Product.objects.filter(addDate__day=currentDay).count(),
        })
    elif request.user.role == "AD":
        return HttpResponseRedirect('/admin/')
    elif request.user.role == "SP":
        my_id = request.user.id
        try:
            supplier_id = Supplier.objects.select_related('owner').get(owner_id=my_id)
            return render(request, "dashboardSP.html",{
                'my_id': my_id,
                'supplier_id': supplier_id.id,
                'product_count': Product.objects.filter(supplier=supplier_id).count(),
                'category': Category.objects.prefetch_related('product').filter(product__supplier_id=supplier_id).count(),
                'brand': Brand.objects.prefetch_related('product').filter(product__supplier_id=supplier_id).count(),
                'transaksi_setahun': Order.objects.filter(orderDate__year=currentYear, supplier=supplier_id).count(),
                'tinjau': Order.objects.filter(isApprove=False, supplier=supplier_id).count(),
                'penawaran_today': Penawaran.objects.filter(tawarDate__day=currentDay, tujuan=my_id).count(),
            })
        except:
            return HttpResponse('Akun anda belum tervalidasi dengan data supplier, silahkan hubungi admin')
             
    else:
        return HttpResponse('Akun anda belum tervalidasi dengan data role, silahkan hubungi admin')

@login_required
def bengkel(request):
    if request.user.role == "LB":
        my_id = request.user.id
        bengkel_id = Bengkel.objects.select_related('owner').get(owner_id=my_id).id
        return HttpResponseRedirect('/bengkel/'+str(bengkel_id))
    else:
        return render(request, "bengkel.html",{
            'bengkel': Bengkel.objects.select_related("owner").all(),
        })

@login_required
def bengkelDetail(request, bengkel_id):
    bengkel = Bengkel.objects.select_related("owner").get(id=bengkel_id)
    return render(request, "bengkelDetail.html",{
        'bengkel': bengkel,
        # 'stock': Stock.objects.select_related("product").filter(bengkel=bengkel_id),
        'stock': Stock.objects.prefetch_related("product__brand","product__category","product__supplier").filter(bengkel=bengkel_id),
    })

@login_required
def editBengkel(request, bengkel_id, stock_id):
    return render(request, "editStock.html",{
        'stock': Stock.objects.prefetch_related("product__brand","product__category","product__supplier").get(id=stock_id),
    })

@login_required
def saveStock(request, stock_id):
    stock = Stock.objects.select_related("bengkel").get(id=stock_id)
    if request.user.role == "SV":

        minStock = int(request.POST['minStock'])
        stock.minStock = minStock
        stock.save()
        
        return HttpResponseRedirect('/bengkel/'+str(stock.bengkel.id),{
            'message': "Data Berhasil disimpan", #ga bisa njir
        })
    elif request.user.role == "LB":
        stockCount = int(request.POST['stockCount'])
        stock.stockCount = stockCount
        stock.save()
        
        return HttpResponseRedirect('/bengkel/'+str(stock.bengkel.id),{
            'message': "Data Berhasil disimpan", #ga bisa njir
        })

@login_required
def supplier(request):
    return render(request, "supplier.html",{
        'supplier': Supplier.objects.select_related("owner").all(),
        # 'tes': Supplier.objects.values(),
    })

@login_required
def supplierDetail(request, supplier_id):
    supplier = Supplier.objects.select_related("owner").get(id=supplier_id)
    return render(request, "supplierDetail.html",{
        'supplier': supplier,
        # 'stock': Stock.objects.select_related("product").filter(bengkel=bengkel_id),
        'product': Product.objects.prefetch_related("category","brand").filter(supplier=supplier_id),
    })


@login_required
def transaksi(request):
    if request.user.role == "SV":
        return render(request, "transaksi.html",{
            'transaksi': Order.objects.select_related("supplier").all(),
            })
    elif request.user.role == "SP":
        my_id = request.user.id
        supplier_id = Supplier.objects.select_related('owner').get(owner_id=my_id).id
        return render(request, "transaksi.html",{
            'transaksi': Order.objects.select_related("supplier").filter(supplier=supplier_id),
            })
    else:
        return HttpResponseRedirect('dashboard/')

@login_required
def transaksiDetail(request, order_id):
    order = Order.objects.get(id=order_id)
    if request.method == 'POST':
        form = TransaksiForm(request.POST, request.FILES)
        form.instance.id = order.id
        form.instance.supplier = order.supplier
        form.instance.bengkel = order.bengkel
        form.instance.orderDate = order.orderDate
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/transaksi/')
            # return HttpResponseRedirect('/transaksi/'+str(order_id))
    else:
          form =  TransaksiForm
    return render(request, 'transaksiDetail.html',{
                'order': order,
                'form':form,
                'transaksi': OrderItem.objects.prefetch_related("orderId","product", "product__brand","product__category",).filter(orderId_id=order_id),
            })

@login_required
def terimaOrder(request, order_id):
    order = Order.objects.get(id=order_id)
    order.isApprove = True
    order.save()
    
    return HttpResponseRedirect('/transaksi/')
    
class TransaksiCreate(LoginRequiredMixin, CreateView):
    model = Order
    template_name = "transaksiCreate.html"
    form_class = TransaksiBaru
    
    def get_success_url(self, **kwargs):
        order1 = Order.objects.first().id
        # order1 += 1   
        return reverse('transaksiItemCreate', args=[order1])

@login_required
def transaksiItemCreate(request, order_id):
    order = Order.objects.get(id=order_id)
    if request.method == 'POST':
        form = TransaksiItem(request.POST, request.user)
        form.instance.orderId = order
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/transaksi/')
            # return HttpResponseRedirect('/transaksi/'+str(order_id))
    else:
          form =  TransaksiItem
    return render(request, 'transaksiItem.html',{
                'order': order,
                'form':form,
                'transaksi': OrderItem.objects.prefetch_related("orderId","product", "product__brand","product__category",).filter(orderId_id=order_id),
            })


@login_required
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('index'))

# @login_required
# class createTransaksi()

@login_required
def penawaran(request, account):
    return render(request, "penawaran.html",{
        'penawaran': Penawaran.objects.filter(Q(tujuan_id=account) | Q(penawar_id=account)),
    })


class PenawaranCreate(LoginRequiredMixin, CreateView):
    model = Penawaran
    template_name = "penawaranCreate.html"
    form_class = PenawaranForm


    def form_valid(self, form):
        form.instance.penawar = (self.request.user)
        return super().form_valid(form)


@login_required
def editAccount(request, account_name):
    return render(request, "profile.html",{})

@login_required
def saveAccount(request, account_name):
    account = Account.objects.get(username=account_name)
    account.username = (request.POST['username'])
    account.set_password(request.POST['password'])
    account.name = (request.POST['name'])
    account.address = (request.POST['address'])
    account.phone = (request.POST['phone'])
    account.telegram = (request.POST['telegram'])
    account.save()
    
    return HttpResponseRedirect('/dashboard/',{
        'message': "Data Berhasil disimpan", #ga bisa njir
    })

# category
class AddCategoryView(LoginRequiredMixin, CreateView):
    model = Category
    template_name = 'add_category.html'
    form_class = AddCategoryForm
    success_url = reverse_lazy('CategoryView')

class UpdateCategoryView(LoginRequiredMixin, UpdateView):
    model = Category
    template_name = 'add_category.html'
    form_class = UpdateCategoryForm
    success_url = reverse_lazy('CategoryView')

class DeleteCategoryView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'delete_category.html'
    success_url = reverse_lazy('CategoryView')

class CategoryView(LoginRequiredMixin, ListView):
    model = Category
    template_name = "category.html"


class AddBrandView(LoginRequiredMixin, CreateView):
    model = Brand
    template_name = 'add_brand.html'
    form_class = AddBrandForm
    success_url = reverse_lazy('BrandView')

class UpdateBrandView(LoginRequiredMixin, UpdateView):
    model = Brand
    template_name = 'add_brand.html'
    form_class = UpdateBrandForm
    success_url = reverse_lazy('BrandView')

class DeleteBrandView(LoginRequiredMixin, DeleteView):
    model = Brand
    template_name = 'delete_Brand.html'
    success_url = reverse_lazy('BrandView')

class BrandView(LoginRequiredMixin, ListView):
    model = Brand
    template_name = "brand.html"


class AddProductView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'add_product.html'
    form_class = AddProductForm
    success_url = reverse_lazy('ProductView')

    def form_valid(self,form):
        my_id = self.request.user.id
        supplier_id = Supplier.objects.select_related('owner').get(owner_id=my_id)
        form.instance.supplier = supplier_id
        return super().form_valid(form)

class UpdateProductView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'add_product.html'
    form_class = UpdateProductForm
    success_url = reverse_lazy('ProductView')

class DeleteProductView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'delete_product.html'
    success_url = reverse_lazy('ProductView')

class ProductView( LoginRequiredMixin, ListView):
    template_name = "product.html"
    def get_queryset(self):
        my_id = self.request.user.id
        supplier_id = Supplier.objects.select_related('owner').get(owner_id=my_id).id
        return Product.objects.filter(supplier= supplier_id)
    
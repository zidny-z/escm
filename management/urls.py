from django.urls import path
from . import views
from management.views import *
# from management.views import PenawaranCreate, TransaksiCreate

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),

    path("bengkel/", views.bengkel, name="bengkel"),
    path("bengkel/<str:bengkel_id>/", views.bengkelDetail, name="bengkelDetail"),
    path("bengkel/<str:bengkel_id>/edit/<str:stock_id>/", views.editBengkel, name="editBengkel"),

    path("bengkel/stock/<str:stock_id>/save", views.saveStock, name="saveStock"),

    path("supplier/<str:supplier_id>", views.supplierDetail, name="supplierDetail"),
    path("supplier/", views.supplier, name="supplier"),

    path("transaksi/", views.transaksi, name='transaksi'),
    path("transaksi/<str:order_id>", views.transaksiDetail, name="transaksiDetail"),
    path("transaksi/<str:order_id>/terima", views.terimaOrder, name="terimaOrder"),
    
    # path("transaksi/create/", views.transaksiCreate, name="transaksiCreate"),
    path("transaksi/create/", TransaksiCreate.as_view(), name="transaksiCreate"),
    path("transaksi/create/<int:order_id>", views.transaksiItemCreate, name="transaksiItemCreate"),
    
    path("penawaran/<str:account>/", views.penawaran, name="penawaran"),
    path("penawaran/<str:account>/create", PenawaranCreate.as_view(), name="penawaranCreate"),

    path("account/<str:account_name>",views.editAccount, name="editAccount"),
    path("account/<str:account_name>/save",views.saveAccount, name="saveAccount"),

    path("category/", CategoryView.as_view(), name="CategoryView"),
    path("category/create", AddCategoryView.as_view(), name="AddCategoryView"),
    path("category/update/<int:pk>", UpdateCategoryView.as_view(), name="UpdateCategoryView"),
    path("category/delete/<int:pk>", DeleteCategoryView.as_view(), name="DeleteCategoryView"),

    path("brand/", BrandView.as_view(), name="BrandView"),
    path("brand/create", AddBrandView.as_view(), name="AddBrandView"),
    path("brand/update/<int:pk>", UpdateBrandView.as_view(), name="UpdateBrandView"),
    path("brand/delete/<int:pk>", DeleteBrandView.as_view(), name="DeleteBrandView"),

    path("product/", ProductView.as_view(), name="ProductView"),
    path("product/create", AddProductView.as_view(), name="AddProductView"),
    path("product/update/<int:pk>", UpdateProductView.as_view(), name="UpdateProductView"),
    path("product/delete/<int:pk>", DeleteProductView.as_view(), name="DeleteProductView"),


]

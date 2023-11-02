import random

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from app.models import Transaction


def index(request):
    if request.user.is_authenticated:
        return redirect('/account')
    else:
        return render(request, 'index.html')


def account(request):
    user = request.user
    if not user.is_authenticated:
        return redirect("/")

    transactions = Transaction.objects.filter(user=user).order_by("-id")

    paginator = Paginator(transactions, 10)

    page = 1
    if request.GET.get("page"):
        page = int(request.GET.get("page"))

    page_obj = paginator.get_page(page)
    transactions = page_obj.object_list

    return render(request, 'account.html', {
        "user": user,
        "transactions": transactions,
        "number_of_pages": paginator.num_pages,
        "pages": paginator.page_range,
        "current_page": page,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
        "previous_page": page - 1,
        "next_page": page + 1,
    })


def create_view(request):
    user = request.user
    if not user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        if request.POST.get("type", "") == "expense":
            Transaction.objects.create(
                user=user,
                description=request.POST.get("description", ""),
                amount=-abs(int(request.POST.get("amount", 0))),
            )
        if request.POST.get("type", "") == "income":
            Transaction.objects.create(
                user=user,
                description=request.POST.get("description", ""),
                amount=abs(int(request.POST.get("amount", 0))),
            )
        return redirect("/")

    raise NotImplementedError


def delete_view(request: HttpRequest, transaction_id: int) -> HttpResponse:
    Transaction.objects.filter(id=transaction_id).filter(user=request.user).delete()
    return redirect("/")


def edit_view(request: HttpRequest, transaction_id: int) -> HttpResponse:
    transaction = Transaction.objects.filter(id=transaction_id).filter(user=request.user).first()

    if request.method == "POST":
        transaction.description = request.POST.get("description", "")
        if request.POST.get("type", "") == "expense":
            transaction.amount = -abs(int(request.POST.get("amount", 0)))
        if request.POST.get("type", "") == "income":
            transaction.amount = abs(int(request.POST.get("amount", 0)))
        transaction.save()
        return redirect("/")

    raise NotImplementedError


def add10(request):
    user = request.user
    if not user.is_authenticated:
        return redirect("/")

    random_description_expenses = [
        "Bought a new car",
        "Bought a new house",
        "Bought a new phone",
        "Bought a new computer",
        "Bought a new notebook",
        "Bought a new TV",
        "Bought a new fridge",
        "Bought a new microwave",
        "Bought a new toaster",
    ]

    random_description_income = [
        "Got a salary",
        "Got a bonus",
        "Got a gift",
        "Got a lottery",
    ]

    for i in range(10):
        Transaction.objects.create(
            user=user,
            description=random.choice(random_description_expenses),
            amount=-abs(random.randint(100, 1000)),
        )

    for i in range(5):
        Transaction.objects.create(
            user=user,
            description=random.choice(random_description_income),
            amount=abs(random.randint(1000, 5000))
        )

    return redirect("/")

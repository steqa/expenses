function categoryShow (categoryPk, expensePk) {
    document.getElementById(`category-opened${ categoryPk }${ expensePk }`).classList.toggle('hidden')
    document.getElementById(`category-closed${ categoryPk }${ expensePk }`).classList.toggle('hidden')
}
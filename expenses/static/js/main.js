const categoryNames = document.querySelectorAll('[data-category-name]');
const categoryNamesOpen = document.querySelectorAll('[data-category-name-open]');

categoryNames.forEach(function (item) {
    item.addEventListener('click', function () {
        item.classList.toggle('hidden')
        const openCategoryName = document.querySelector('#' + this.dataset.categoryName);
        openCategoryName.classList.toggle('hidden')
    });
});

categoryNamesOpen.forEach(function (item) {
    item.addEventListener('click', function () {
        item.classList.toggle('hidden')
        const categoryName = document.querySelector('#' + this.dataset.categoryNameOpen);
        categoryName.classList.toggle('hidden')
    });
});
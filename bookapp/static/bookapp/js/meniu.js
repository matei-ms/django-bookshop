document.addEventListener('DOMContentLoaded', function () {
    var dropdowns = document.querySelectorAll('.menu > li.dropdown');

    dropdowns.forEach(function (dropdown) {
        var link = dropdown.querySelector(':scope > a');

        link.addEventListener('click', function (e) {
            if (!dropdown.classList.contains('open')) {
                e.preventDefault();

                dropdowns.forEach(function (other) {
                    if (other !== dropdown) {
                        other.classList.remove('open');
                    }
                });

                dropdown.classList.add('open');
            }
        });
    });

    document.addEventListener('click', function (e) {
        if (!e.target.closest('.dropdown')) {
            dropdowns.forEach(function (dropdown) {
                dropdown.classList.remove('open');
            });
        }
    });
});

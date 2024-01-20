// Проверяем, находимся ли мы на главной странице
console.log("script js")
console.log(window.location.pathname)


// Проверяем, находится ли скрипт на странице / (главной странице)

function animateBar() {
    // Функция для генерации случайного числа от min до max
    function getRandomInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    // Функция для установки случайной ширины элемента
    function setRandomWidth() {
        var bar = document.getElementById('bar');
        var endLevelElement = document.getElementById('ex_end_value');
        var randomValue = getRandomInt(1, endLevelElement.textContent);
        var percent = randomValue / endLevelElement.textContent * 100;
        animateNumber(randomValue);
        var randomWidth = percent + '%';
        bar.style.width = randomWidth;
    }

    // Вызываем функцию каждую секунду
    setInterval(setRandomWidth, 1000);
}

function animateLvl() {
    // Получаем элемент по id
    var levelElement = document.getElementById('lvl');
    var endLevelElement = document.getElementById('ex_end_value');

    // Устанавливаем начальное значение
    var level = 1;

    // Функция для увеличения значения и обновления элемента
    function incrementLevel() {
        level++;
        levelElement.textContent = level;
        endLevelElement.textContent = 100 * Math.pow(level, 2);
    }

    // Устанавливаем интервал вызова функции каждую секунду
    var intervalId = setInterval(incrementLevel, 1000);

    // Пример: остановить увеличение после 10 секунд (вы можете убрать этот блок, если хотите бесконечное увеличение)
    setTimeout(function () {
        clearInterval(intervalId);
    }, 100000);
}

// Функция для анимации увеличения или уменьшения числа
function animateNumber(targetValue) {
    var element = document.getElementById('ex_value');
    var startValue = parseInt(element.textContent, 10);
    var duration = 700; // длительность анимации в миллисекундах
    var startTime;

    function updateNumber(timestamp) {
        if (!startTime) startTime = timestamp;
        var progress = timestamp - startTime;
        var value = Math.floor(startValue + (targetValue - startValue) * (progress / duration));

        element.textContent = value;

        if (progress < duration) {
            requestAnimationFrame(updateNumber);
        }
    }

    requestAnimationFrame(updateNumber);
}

// Вызовите функцию с целевым значением (например, 100)
animateNumber(100);
if (window.location.pathname === "/hello") {
    animateBar();
    animateLvl();
}


    function updateExpValue(userId, DOMElementID, userLvl) {
    // Переменная для отслеживания времени (в миллисекундах)
    console.log(userId + " " + $('#' + DOMElementID).text());
    // Запускаем цикл обновления каждые 5 секунд
    var intervalId = setInterval(function () {
        // Получаем текущее время
        var currentTime = new Date().getTime();

        // Если не прошло 5 секунд, обновляем значение поля DOM объекта

        // Получаем значение exp из пользователя с указанным id
        // Это может потребовать использования AJAX-запроса к серверу, чтобы получить актуальное значение exp

        // Здесь предполагается, что вы имеете функцию, которая выполняет AJAX-запрос к серверу для получения значения exp по id пользователя
        getExpValueFromServer(userId)
            .then(function (expValue) {
                $('#' + DOMElementID).text(expValue);
                $('#' + DOMElementID + 'bar').width(expValue/(100*(userLvl**2))*100 +'%');
                if (expValue > 100*(userLvl**2)) {

                    location.reload();
                }
            })
            .catch(function (error) {
            });

    }, 1000); // Проверка каждую секунду
}

// Пример функции для выполнения AJAX-запроса
function getExpValueFromServer(userId) {
    return new Promise(function (resolve, reject) {
        $.ajax({
            url: '/get_exp',
            method: 'GET',
            data: {userId: userId},
            async: true,
            success: function (data) {
                resolve(data.exp);
            },
            error: function () {
                reject('Failed to get exp value from the server');
            }
        });
    });
}


const daysTag = document.querySelector(".days"),
currentDate = document.querySelector(".current-date"),
prevNextIcon = document.querySelectorAll(".icons span");

// getting new date, current year and month
let date = new Date(),
currYear = date.getFullYear(),
currMonth = date.getMonth();

// storing full name of all months in array
const months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"];

const renderCalendar = () => {
    let firstDayofMonth = new Date(currYear, currMonth, 1).getDay(), // getting first day of month
    lastDateofMonth = new Date(currYear, currMonth + 1, 0).getDate(), // getting last date of month
    lastDayofMonth = new Date(currYear, currMonth, lastDateofMonth).getDay(), // getting last day of month
    lastDateofLastMonth = new Date(currYear, currMonth, 0).getDate(); // getting last date of previous month
    let liTag = "";

    for (let i = firstDayofMonth; i > 0; i--) { // creating li of previous month last days
        liTag += `<li class="inactive">${lastDateofLastMonth - i + 1}</li>`;
    }

    for (let i = 1; i <= lastDateofMonth; i++) { // creating li of all days of current month
        // adding active class to li if the current day, month, and year matched
        let isToday = i === date.getDate() && currMonth === new Date().getMonth()
                     && currYear === new Date().getFullYear() ? "active" : "";
        liTag += `<li class="${isToday}">${i}</li>`;
    }

    for (let i = lastDayofMonth; i < 6; i++) { // creating li of next month first days
        liTag += `<li class="inactive">${i - lastDayofMonth + 1}</li>`
    }
    currentDate.innerText = `${months[currMonth]} ${currYear}`; // passing current mon and yr as currentDate text
    daysTag.innerHTML = liTag;
}
renderCalendar();

prevNextIcon.forEach(icon => { // getting prev and next icons
    icon.addEventListener("click", () => { // adding click event on both icons
        // if clicked icon is previous icon then decrement current month by 1 else increment it by 1
        currMonth = icon.id === "prev" ? currMonth - 1 : currMonth + 1;

        if(currMonth < 0 || currMonth > 11) { // if current month is less than 0 or greater than 11
            // creating a new date of current year & month and pass it as date value
            date = new Date(currYear, currMonth, new Date().getDate());
            currYear = date.getFullYear(); // updating current year with new date year
            currMonth = date.getMonth(); // updating current month with new date month
        } else {
            date = new Date(); // pass the current date as date value
        }
        renderCalendar(); // calling renderCalendar function
    });
});

function convertMonthToNumber(monthString) {
    // Crea un oggetto o un array che mappa i nomi dei mesi ai numeri
    let monthMap = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12
    }


    // Converte la stringa del mese in minuscolo e rimuove eventuali spazi extra
    let lowercaseMonth = monthString.toLowerCase().trim();

    // Restituisce il numero corrispondente al mese
    return monthMap[lowercaseMonth];
}
function confrontaDate(data1, data2) {
    // Estrarre i valori di anno, mese e giorno dalle date
    const anno1 = data1.getFullYear();
    const mese1 = data1.getMonth();
    const giorno1 = data1.getDate();

    const anno2 = data2.getFullYear();
    const mese2 = data2.getMonth();
    const giorno2 = data2.getDate();

    // Confronto dell'anno
    if (anno1 < anno2) {
        return -1;
    } else if (anno1 > anno2) {
        return 1;
    }

    // Confronto del mese
    if (mese1 < mese2) {
        return -1;
    } else if (mese1 > mese2) {
        return 1;
    }

    // Confronto del giorno
    if (giorno1 < giorno2) {
        return -1;
    } else if (giorno1 > giorno2) {
        return 1;
    }

    // Le date sono uguali
    return 0;
}

$(document).ready(function() {
    let mese = convertMonthToNumber($('.current-date').text().split(" ")[0]);
    let anno = $('.current-date').text().split(" ")[1];
    getUserMonthEvents(anno, mese);
    let isSpan

    $(document).on('mouseenter', 'li:not(.inactive):not(.day-of-week)', function() {
        let originalText = $(this).text();
        $(this).data('originalText', originalText);

        isSpan=false
        if($(this).find('.event-indicator').length !== 0){
          isSpan = true;
          $(this).empty().append("<i class='fas fa-eye'></i>")
        }
        else
            $(this).text('+');
    });

    $(document).on('mouseleave', 'li:not(.inactive):not(.day-of-week)', function() {
      let originalText = $(this).data('originalText');
      $(this).text(originalText);
        if(isSpan === true){
            let $eventIndicator = $("<span class='event-indicator'></span>");
            if ($(this).hasClass('active')) {
                $eventIndicator.css('background-color', 'white');
            }
            $(this).append($eventIndicator);
            isSpan=false
        }
    });

    // Funzione per ottenere gli eventi di un mese e anno specifici per l'utente dalla sessione
    function getUserMonthEvents(anno, mese) {
        let url = "/events?mese=" + mese + "&anno=" + anno;
        $.get(url, function(response) {
            // Etichetta i giorni del calendario relativi agli eventi ottenuti
            response.forEach(function(event) {

                let dataInizio = new Date(event.data_inizio);
                let dataFine = new Date(event.data_fine);
                let giorni = getDaysArray(dataInizio, dataFine, mese);

               //console.log(giorni);
                giorni.forEach(function(giorno) {
                    let giornoNumero = giorno.getDate();
                    let $dayElement = $(".calendar .days li:not(.inactive)").filter(function() {
                        //console.log(event.id);
                        $(this).attr('event-id', event.id);
                        return $(this).text().trim() === giornoNumero.toString();
                    });

                    $($dayElement).attr('event-id', event._id);
                    if (!$dayElement.find('.event-indicator').length) {
                        let $eventIndicator = $("<span class='event-indicator'></span>");
                        if ($dayElement.hasClass('active')) {
                            $eventIndicator.css('background-color', 'white');
                        }
                        $dayElement.append($eventIndicator);
                    }
                });
            });
        })
    }
    // Funzione per ottenere un array di date tra la data di inizio e la data di fine inclusi
    function getDaysArray(dataInizio, dataFine, mese) {
        let arr = [];
        let currDate = new Date(dataInizio);
        while (confrontaDate(currDate, dataFine) <= 0 ) {
            //console.log(currDate)
            if (currDate.getMonth() === mese - 1) {

                arr.push(new Date(currDate));
            }
            currDate.setDate(currDate.getDate() + 1);


        }
        return arr;
    }

    // Associa il gestore di eventi al clic sulla classe "next"
    $('.icons').click(function() {
        let mese = convertMonthToNumber($('.current-date').text().split(" ")[0]);
        let anno = $('.current-date').text().split(" ")[1];
        getUserMonthEvents(anno, mese);
    });

    $(document).on('click', 'li:not(.inactive):not(.day-of-week)', function() {
        let url;
        let day = $(this).data('originalText');
        let month = convertMonthToNumber($('.current-date').text().split(" ")[0]);
        let year = $('.current-date').text().split(" ")[1];

        if($(this).find('i').length !== 0){
            url = '/update-event?event-id=' + $(this).attr('event-id');
        }
        else {
            url = '/insert-event?day=' + encodeURIComponent(day) + '&month=' + encodeURIComponent(month) + '&year=' + encodeURIComponent(year);
        }


        window.location.href = url;
  });

});
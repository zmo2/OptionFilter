$(document).ready(function () {


    $("#getStr").on("click", function (event) {
        event.preventDefault()
        const queryUrl = "http://127.0.0.1:5000/optionchains/AAPL"

        $.ajax({
            url: queryUrl,
            method: "GET",
            dataType: "jsonp",
            data: {},
        }).then(function (res) {
            $(".results").append(res)
            console.log(res)
        })
    })

})
$(document).ready(function () {


    $("#getStr").on("click", function (event) {
        event.preventDefault()
        const queryUrl = "http://127.0.0.1:5000/optionchains/AAPL"

        $.ajax({
            url: queryUrl,
            method: "GET",
        }).then(function (res) {
            $(".results").text(res["OptionChainResponse"]["OptionPair"][0]["Call"]["displaySymbol"])
            console.log(res["OptionChainResponse"]["OptionPair"][0]["Call"])
        })
    })

})
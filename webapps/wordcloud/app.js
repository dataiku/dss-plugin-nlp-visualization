let allRows;
let webAppConfig = dataiku.getWebAppConfig()['webAppConfig'];
let webAppDesc = dataiku.getWebAppDesc()['chart'];

window.parent.postMessage("sendConfig", "*");

function set_simple_svg(){
    let headers = new Headers()
    let init = {
        method : 'GET',
        headers : headers
    }

    let url = getWebAppBackendUrl('/get_svg')
    fetch(url, init)
    .then(function(response){
        response.json()
        .then(function(data){
            document.getElementById('wordcloud').innerHTML = data.svg;
        })
    })
    console.log("Hello !");
}

window.addEventListener('message', function(event) {
    if (event.data) {

        event_data = JSON.parse(event.data);
        webAppConfig = event_data['webAppConfig']
        console.log(webAppConfig);

        // TODO catch when filter all alphanum column type values
        try {
            checkWebAppParameters(webAppConfig, webAppDesc);
        } catch (e) {
            dataiku.webappMessages.displayFatalError(e.message);
            return;
        }

        try {
            checkWebAppConfig(webAppConfig)
        } catch (e) {
            dataiku.webappMessages.displayFatalError(e.message);
            return;
        }
                

        set_simple_svg();
    } 
 });
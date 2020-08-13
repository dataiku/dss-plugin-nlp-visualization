let allRows;
let webAppConfig = dataiku.getWebAppConfig()['webAppConfig'];

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

        set_simple_svg();
    } 
 });
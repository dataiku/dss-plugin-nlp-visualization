let allRows;
let webAppConfig = dataiku.getWebAppConfig()['webAppConfig'];
let webAppDesc = dataiku.getWebAppDesc()['chart']

window.parent.postMessage("sendConfig", "*");

function set_simple_svg(params){
    let headers = new Headers();
    let init = {
        method : 'GET',
        headers : headers
    };
    let url = getWebAppBackendUrl('/get_svg')+'/'+JSON.stringify(params);

    fetch(url, init)
    .then(function(response){
        response.json()
        .then(function(data){
            for (var chart of data) {
								
                var title = document.createElement('div');
                title.innerHTML = chart.subchart;
                title.setAttribute('class', 'sep');
                document.getElementById('wordcloud').appendChild(title);
                
                var worcloud = document.createElement('div');
                worcloud.innerHTML = chart.svg;
                worcloud.setAttribute('class', 'wordcloud');
                document.getElementById('wordcloud').appendChild(worcloud);
            }
        })
    })
}

window.addEventListener('message', function(event) {
    if (event.data) {

        event_data = JSON.parse(event.data);

        // Load webapp config
        webAppConfig = event_data['webAppConfig'];

        var params = {
            dataset_name: webAppConfig['dataset'],
            text_column: webAppConfig['text_column'],
            language: webAppConfig['language'],
            subchart_column: webAppConfig['subchart_column']
        }

        console.log(webAppConfig);

        // Check webapp config
        try {
            checkWebAppParameters(webAppConfig, webAppDesc);
        } catch (e) {
            dataiku.webappMessages.displayFatalError(e.message);
            return;
        }

        // Clear previous webapp HTML
        var div = document.getElementById('wordcloud');
        while(div.firstChild){
            div.removeChild(div.firstChild);
        }

        // Load new webapp HTML
        set_simple_svg(params);
    } 
 });
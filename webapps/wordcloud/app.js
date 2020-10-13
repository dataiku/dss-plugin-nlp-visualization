let allRows;
let webAppConfig = dataiku.getWebAppConfig()['webAppConfig'];
let webAppDesc = dataiku.getWebAppDesc()['chart']

window.parent.postMessage("sendConfig", "*");

function set_simple_svg(params) {
    let headers = new Headers();
    let init = {
        method: 'GET',
        headers: headers
    };
    let url = getWebAppBackendUrl('/get_svg') + '/' + JSON.stringify(params);

    fetch(url, init)
        .then(function (response) {
            response.json()
                .then(function (data) {
                    document.getElementById("spinner").style.display = "none";
                    for (var chart of data) {

                        var row = document.createElement('div');
                        row.setAttribute('class', 'row')

                        var col = document.createElement('div');
                        col.setAttribute('class', 'col')
                        row.appendChild(col)

                        var worcloud = document.createElement('div');
                        worcloud.innerHTML = chart.svg;
                        worcloud.setAttribute('class', 'single-chart');
                        col.appendChild(worcloud);

                        document.getElementById('wordcloud').appendChild(row);
                    }
                })
        })
}

function set_subcharts_svg(params) {
    let headers = new Headers();
    let init = {
        method: 'GET',
        headers: headers
    };
    let url = getWebAppBackendUrl('/get_svg') + '/' + JSON.stringify(params);

    fetch(url, init)
        .then(function (response) {
            response.json()
                .then(function (data) {
                    document.getElementById("spinner").style.display = "none";
                    var progress_total = data.length
                    var progress_state = 0
                    var progress = 0
                    /*
                                        function some_3secs_function(progress_state, progress_total, progress, callback) {
                                            function progress_loop() {         //  create a loop function
                                                setTimeout(function () {   //  call a 3s setTimeout when the loop is called
                                                    console.log('hello');   //  your code here
                                                    progress_state++;
                                                    progress = parseInt((progress_state / progress_total) * 100);
                                                    $('.progress-bar').css('width', progress + '%').attr('aria-valuenow', progress);
                                                    $('.progress-bar-label').text(progress + '%');                  //  increment the counter
                                                    if (progress_state < progress_total) {           //  if the counter < 10, call the loop function
                                                        progress_loop();             //  ..  again which will trigger another 
                                                    }                       //  ..  setTimeout()
                                                }, 2000)
                                            }
                    
                                            progress_loop();
                                            callback();
                                        };
                                        function some_5secs_function(data) {
                                            for (var chart of data) {
                    
                                                var row = document.createElement('div');
                                                row.setAttribute('class', 'row subcharts')
                    
                                                var title = document.createElement('div');
                                                title.innerHTML = chart.subchart;
                                                title.setAttribute('class', 'col-md-2 align-self-center');
                                                row.appendChild(title);
                    
                                                var worcloud = document.createElement('div');
                                                worcloud.innerHTML = chart.svg;
                                                worcloud.setAttribute('class', 'col-md-10 py-4');
                                                row.appendChild(worcloud);
                    
                                                document.getElementById('wordcloud').appendChild(row);
                                            }
                                        };
                    
                                        some_3secs_function(progress_state, progress_total, progress, function () {
                                            some_5secs_function(data);
                                        });
                    
                    
                                        /*
                                                            some_3secs_function(data, function () {
                                                                function progress_loop() {         //  create a loop function
                                                                    setTimeout(function () {   //  call a 3s setTimeout when the loop is called
                                                                        console.log('hello');   //  your code here
                                                                        progress_state++;
                                                                        progress = parseInt((progress_state / progress_total) * 100);
                                                                        $('.progress-bar').css('width', progress + '%').attr('aria-valuenow', progress);
                                                                        $('.progress-bar-label').text(progress + '%');                  //  increment the counter
                                                                        if (progress_state < progress_total) {           //  if the counter < 10, call the loop function
                                                                            progress_loop();             //  ..  again which will trigger another 
                                                                        }                       //  ..  setTimeout()
                                                                    }, 1000)
                                                                }
                                        
                                                                progress_loop();
                                                                some_5secs_function(data, function () {
                                                                    for (var chart of data) {
                                        
                                                                        var row = document.createElement('div');
                                                                        row.setAttribute('class', 'row subcharts')
                                        
                                                                        var title = document.createElement('div');
                                                                        title.innerHTML = chart.subchart;
                                                                        title.setAttribute('class', 'col-md-2 align-self-center');
                                                                        row.appendChild(title);
                                        
                                                                        var worcloud = document.createElement('div');
                                                                        worcloud.innerHTML = chart.svg;
                                                                        worcloud.setAttribute('class', 'col-md-10 py-4');
                                                                        row.appendChild(worcloud);
                                        
                                                                        document.getElementById('wordcloud').appendChild(row);
                                                                    }
                                                                });
                                                            });
                                                            /*
                                                                                var i = 1;                  //  set your counter to 1
                                                            */

                    function progress_loop() {         //  create a loop function
                        setTimeout(function () {   //  call a 3s setTimeout when the loop is called
                            console.log('hello');   //  your code here
                            progress_state++;
                            progress = parseInt((progress_state / progress_total) * 100);
                            $('.progress-bar').css('width', progress + '%').attr('aria-valuenow', progress);
                            $('.progress-bar-label').text(progress + '%');                  //  increment the counter
                            if (progress_state < progress_total) {           //  if the counter < 10, call the loop function
                                progress_loop();             //  ..  again which will trigger another 
                            }                       //  ..  setTimeout()
                        }, 3000)
                    };

                    function generate_charts(data) {
                        for (var chart of data) {

                            var row = document.createElement('div');
                            row.setAttribute('class', 'row subcharts')

                            var title = document.createElement('div');
                            title.innerHTML = chart.subchart;
                            title.setAttribute('class', 'col-md-2 align-self-center');
                            row.appendChild(title);

                            var worcloud = document.createElement('div');
                            worcloud.innerHTML = chart.svg;
                            worcloud.setAttribute('class', 'col-md-10 py-4');
                            row.appendChild(worcloud);

                            document.getElementById('wordcloud').appendChild(row);
                        }
                    };
                    progress_loop();
                    generate_charts(data);

                })
        })
}

window.addEventListener('message', function (event) {
    if (event.data) {

        event_data = JSON.parse(event.data);

        // Load webapp config
        webAppConfig = event_data['webAppConfig'];

        var params = {
            dataset_name: webAppConfig['dataset'],
            text_column: webAppConfig['text_column'],
            language: webAppConfig['language'],
            subchart_column: webAppConfig['subchart_column'],
            lemmatize: webAppConfig['lemmatize'],
            tokens_filter: webAppConfig['tokens_filter']
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
        while (div.firstChild) {
            div.removeChild(div.firstChild);
        };

        // Add loader
        document.getElementById("spinner").style.display = "block";

        // Load new webapp HTML
        if (params.subchart_column) {
            set_subcharts_svg(params);
        } else {
            set_simple_svg(params);
        }



    }
});
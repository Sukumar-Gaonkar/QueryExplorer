function switchDB(e){

    switch (e.innerText) {
        case "MySQL":
            document.getElementById("redshift_button").classList.remove("active");
            document.getElementById("mysql_button").classList.add("active");
            document.getElementById("activeDB").value = "MySQL";
            activeDB = "MySQL";
            break;
        case "RedShift":
            document.getElementById("mysql_button").classList.remove("active");
            document.getElementById("redshift_button").classList.add("active");
            document.getElementById("activeDB").value = "RedShift";
            activeDB = "RedShift";
            break;
    }
}

function initQueryExplorer(){
    if(document.getElementById("mysql_button").classList.contains("active"))
        activeDB = "MySQL";
    else
        activeDB = "RedShift";

    document.getElementById("activeDB").value = activeDB
}

function getData(){
    url = "http://localhost";
    $.get(url, function(data, status){
        alert(data);
    });
}
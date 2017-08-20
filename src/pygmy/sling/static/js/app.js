function copyToClipboard(className){
    var clipboard = new Clipboard('.' + className);
    clipboard.on('success', function(e) {
        console.log(e);
    });
    clipboard.on('error', function(e) {
        console.log(e);
    });
}


function readOnlyToggle(elementId) {
    var element = document.getElementById(elementId);
    element.readOnly = !element.readOnly;
}


function displayToggle(elementId) {
    var element = document.getElementById(elementId);
    var displayProperty = "block";
    if(element.style.display == displayProperty){
         displayProperty = "none";
    }
    element.style.display = displayProperty;
}


function UpdateStatus(){

//make an ajax call and get status value using the same 'id'
var var1= document.getElementById("status").value;
$.ajax({

        type:"GET",//or POST
        url:'http://localhost:7080/ajaxforjson/Testajax',
                           //  (or whatever your url is)
        data:{data1:var1},
        //can send multipledata like {data1:var1,data2:var2,data3:var3
        //can use dataType:'text/html' or 'json' if response type expected
        success:function(responsedata){
               // process on data
               alert("got response as "+"'"+responsedata+"'");

        }
     })

}
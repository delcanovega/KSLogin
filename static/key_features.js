var presd_k = 0;
var start_pr;
var avg_key_dw = 0;
var start_fl;
var avg_flight = 0;

$(document).ready(function(){
    $("#q").keydown(function(event){
        if (event.which == 20) {  // Uses bloq. mayus
            $("#f4").val(1);
        }
        start_pr = $.now();
        if (start_fl > 0) {
            var ellapsed_f = $.now() - start_fl;
            avg_flight = (avg_flight * (presd_k-2)) + ellapsed_f;
            avg_flight /= (presd_k - 1);

            $("#f3").val(avg_flight);
        }
    });
    $("#q").keyup(function(){
        presd_k += 1;
        var ellapsed_d = $.now() - start_pr;
        if (ellapsed_d < 1500) {
            avg_key_dw = (avg_key_dw * (presd_k-1)) + ellapsed_d;
            avg_key_dw /= presd_k;

            $("#f1").val(presd_k);
            $("#f2").val(avg_key_dw);

            start_fl = $.now();
        }
        start_pr = 0;
    });
});

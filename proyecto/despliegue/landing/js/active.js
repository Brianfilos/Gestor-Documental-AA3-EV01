$('document').ready(function(){

     //======>  Pricing Toggle Functionality

    $("[class*='btn--toggle']").on('change',function(e){
        
        
        var getTarget = $(this).attr('data-tab-target'); 
        var inpSelect = $(this).children().children('input[type="checkbox"]');

        if($(inpSelect).is(':checked')){
            if($(getTarget).hasClass('monthly')){
                $(getTarget).removeClass('monthly');
                $(getTarget).addClass('yearly');
          
            }
        }else{
            // $(getTarget).removeClass('monthly');
            if($(getTarget).hasClass('yearly')){
                $(getTarget).removeClass('yearly');
                $(getTarget).addClass('monthly');
          
            }
        }      
    })

  
})

//======>  Mobile Menu Activation
$('.main-navigation').meanmenu({
    meanScreenWidth: "992",
    meanMenuContainer: '.mobile-menu',
    meanMenuClose: "<i class='fas fa-times'></i>",
    meanMenuOpen: "<i class='fas fa-bars'></i>",
    meanExpand: "",
});
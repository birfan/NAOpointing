var application = function(){
    
    /*
     * QiSession event
     */
    var services = {};
	var ttstemp;
	var autostate;
	var vX,vY;
	
    var onConnected = function(session){
        console.log("Connected !");
        var acceptable_tries = 10;
		
        function checkConnectionGauge() {
			session.service("ALMemory").done(function (ALMemory) {
				
				//here we set up the subscriber for the touch event
				ALMemory.subscriber("FrontTactilTouched").done(function (subscriber) {
				subscriber.signal.connect(function (state) {
				$(".labelclass").text("Front Tactile");
					});
				});
				ALMemory.subscriber("MiddleTactilTouched").done(function (subscriber) {
				subscriber.signal.connect(function (state) {
				$(".labelclass").text("Middle Tactile");
					});
				});
				ALMemory.subscriber("RearTactilTouched").done(function (subscriber) {
				subscriber.signal.connect(function (state) {
				$(".labelclass").text("Rear Tactile");
					});
				});
			});
            
		RobotUtils.onService(function (PointingService) {
            $("#noservice").hide();
			//defone the service
            services.PointingService = PointingService;
			// Find the button with the right level:
            $(".levelbutton").each(function(level) {
                var button = $(this);
                if (button.data("level") == level) {
                    button.addClass("highlighted");
                    button.addClass("clicked");
                }
            });
				
            $("#buttons").show();
            $(".levelbutton").click(function() {
                // grey out the button, until we hear back that the click worked.
                var button = $(this);
                var level = button.data("level");
                console.log("Button " + level + " clicked");
				if(level==1)
				{
					PointingService.stiffnessOn().then(function(){
	                    button.addClass("highlighted");
						});
				}
				if(level==2)
				{
					PointingService.stiffnessOff().then(function(){
	                    button.addClass("highlighted");
						});
				}
				if(level==3)
				{
					PointingService.subscribeCamera(1).then(function(){
	                    button.addClass("highlighted");
						});
				}
				if(level==4)
				{
					PointingService.unsubscribeCamera().then(function(){
	                    button.addClass("highlighted");
						});
				}
				if(level==5)
				{
					PointingService.pointAtWorld(0.1, 0.1, 0.1, 0.3, 2.5, 0).then(function(){
	                    button.addClass("highlighted");
						});
				}
				if(level==6)
				{
					PointingService.localise(1368, 912).then(function(){
	                    button.addClass("highlighted");
						});
				}
				if(level==7)
				{
					PointingService.pointAtTablet(100, 100, 0.3, 2.5).then(function(){
	                    button.addClass("highlighted");
						});
				}
				if(level==8)
				{
					PointingService.pointAtTag(8, 0.3, 2.5).then(function(){
	                    button.addClass("highlighted");
						});
				}
					
                    
            })
        }, function() {
            // We failed to get the service, wait again, and try again
            // We display an error message after a while.
            if (acceptable_tries > 0) {
                acceptable_tries -= 1;
                setTimeout(checkConnectionGauge, 200);
            } else {
                $("#noservice").show();
                setTimeout(checkConnectionGauge, 2000);
            }
        });
        }
		//track mouse clicks on the page
		$('*').on('click', function (e) {
		// make sure the event isn't bubbling
		if (e.target != this) {
			return;
		}
					
        checkConnectionGauge();

        $("#exit").click(function() {
            if (services.PointingService) {
                services.PointingService.stop();
            }

        });
    };
    
    var onError = function(){
        console.log("Disconnected, or failed to connect :-(");
    }

    RobotUtils.connect(onConnected, onError);
};

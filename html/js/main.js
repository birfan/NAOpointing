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
					//execute directly
					//autostate="solitary";
					//startRobot(autostate);
					PointingService.StartLife().then(function(){
	                    button.addClass("highlighted");
						});
				}
				if(level==2)
				{//execute directly
					//autostate="disabled";
					//startRobot(autostate);
					PointingService.StopLife().then(function(){
	                    button.addClass("highlighted");
						});
				}
				if(level==3)
				{//execute directly
					//var vSpeech = prompt("Say something via NAO", "Hello");
					//speak(vSpeech);
					PointingService.PointAtWorld(0.2,1.0,-1.0,1.0,5.0).then(function(){
					//PointingService.PointAtWorld(0.2,1.0,1.0,0.0).then(function(){
	                    button.addClass("highlighted");
						});
				}
				if(level==4)
				{//use the service to execute a behaviour
					PointingService.PointAtTablet(0.2,100,200,10.0).then(function(){
//					PointingService.PointAtTablet(0.2,100,200).then(function(){
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
		pointing(e.pageX, e.pageY);
		});
		//function for speech
		function speak(ttstemp)
		{
			session.service("ALTextToSpeech").done(function(tts)
			{
				tts.say(ttstemp);
			});
		}
		//function for pointing
		function pointing(vX, vY)
		{
			console.log("X:" + vX + "Y:" + vY);
			$(".labelclass1").text("X: " + vX + " Y: " + vY);
		}
		//function for setting autonomous life
		function startRobot(autostate)
		{
			session.service("ALAutonomousLife").done(function(motionAuto)
			{
				motionAuto.setState(autostate);
			});
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

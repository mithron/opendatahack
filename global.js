function getURLParameter(name) {
        return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null
    }
	
function disableAudio(id) {
		allowed = false; 
		stopAudio(id, allowed); 
	}
	
function stopAudio(id, allowed)  {
        if(document.getElementById('instrPlayer') != null && id != 'instrPlayer' ) {
            document.getElementById('instrPlayer').pause();
            }
        if(document.getElementById('sidebarPlayer') != null && id != 'sidebarPlayer') {
            document.getElementById('sidebarPlayer').pause();
        }
        if(document.getElementById('popupPlayer') != null && id != 'popupPlayer') {
            document.getElementById('popupPlayer').pause();
        }
		if(allowed){
			document.getElementById(id).play();}
		else {			
				document.getElementById(id).pause();
		}
    }	
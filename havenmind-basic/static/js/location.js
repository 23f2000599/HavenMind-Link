// Location sharing for emergency situations
function requestLocationForEmergency() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const latitude = position.coords.latitude;
                const longitude = position.coords.longitude;
                
                // Send location to emergency contact
                fetch('/share-location', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        latitude: latitude,
                        longitude: longitude
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        console.log('Location shared with emergency contact');
                        showLocationAlert('Your live location has been shared with your emergency contact for safety.');
                    } else {
                        console.error('Failed to share location:', data.error);
                    }
                })
                .catch(error => {
                    console.error('Error sharing location:', error);
                });
            },
            function(error) {
                console.error('Geolocation error:', error);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 60000
            }
        );
    }
}

function showLocationAlert(message) {
    alert('📍 ' + message);
}

// Check for negative journal entry and request location
if (window.location.search.includes('request_location=true')) {
    setTimeout(() => {
        requestLocationForEmergency();
    }, 1000);
}
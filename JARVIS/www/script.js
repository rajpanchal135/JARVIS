window.addEventListener("load", windowLoadHandler, false);
var sphereRad = 140;
var radius_sp = 1;
//for debug messages
var Debugger = function () { };
Debugger.log = function (message) {
	try {
		console.log(message);
	}
	catch (exception) {
		return;
	}
}

function windowLoadHandler() {
	canvasApp();
}

function canvasSupport() {
	return Modernizr.canvas;
}

function canvasApp() {
	if (!canvasSupport()) {
		return;
	}

	var theCanvas = document.getElementById("canvasOne");
	var context = theCanvas.getContext("2d");

	var displayWidth;
	var displayHeight;
	var timer;
	var wait;
	var count;
	var numToAddEachFrame;
	var particleList;
	var recycleBin;
	var particleAlpha;
	var r, g, b;
	var fLen;
	var m;
	var projCenterX;
	var projCenterY;
	var zMax;
	var turnAngle;
	var turnSpeed;
	var sphereCenterX, sphereCenterY, sphereCenterZ;
	var particleRad;
	var zeroAlphaDepth;
	var randAccelX, randAccelY, randAccelZ;
	var gravity;
	var rgbString;
	//we are defining a lot of variables used in the screen update functions globally so that they don't have to be redefined every frame.
	var p;
	var outsideTest;
	var nextParticle;
	var sinAngle;
	var cosAngle;
	var rotX, rotZ;
	var depthAlphaFactor;
	var i;
	var theta, phi;
	var x0, y0, z0;

	init();

	// eel.expose(init)
	function init() {
		wait = 1;
		count = wait - 1;
		numToAddEachFrame = 8;

		//particle color
		r = 0;
		g = 72;
		b = 255;

		rgbString = "rgba(" + r + "," + g + "," + b + ","; //partial string for color which will be completed by appending alpha value.
		particleAlpha = 1; //maximum alpha

		displayWidth = theCanvas.width;
		displayHeight = theCanvas.height;

		fLen = 320; //represents the distance from the viewer to z=0 depth.

		//projection center coordinates sets location of origin
		projCenterX = displayWidth / 2;
		projCenterY = displayHeight / 2;

		//we will not draw coordinates if they have too large of a z-coordinate (which means they are very close to the observer).
		zMax = fLen - 2;

		particleList = {};
		recycleBin = {};

		//random acceleration factors - causes some random motion
		randAccelX = 0.1;
		randAccelY = 0.1;
		randAccelZ = 0.1;

		gravity = -0; //try changing to a positive number (not too large, for example 0.3), or negative for floating upwards.

		particleRad = 1.8;

		sphereCenterX = 0;
		sphereCenterY = 0;
		sphereCenterZ = -3 - sphereRad;

		//alpha values will lessen as particles move further back, causing depth-based darkening:
		zeroAlphaDepth = -750;

		turnSpeed = 2 * Math.PI / 1200; //the sphere will rotate at this speed (one complete rotation every 1600 frames).
		turnAngle = 0; //initial angle

		timer = setInterval(onTimer, 10 / 24);
	}

	function onTimer() {
		//if enough time has elapsed, we will add new particles.		
		count++;
		if (count >= wait) {

			count = 0;
			for (i = 0; i < numToAddEachFrame; i++) {
				theta = Math.random() * 2 * Math.PI;
				phi = Math.acos(Math.random() * 2 - 1);
				x0 = sphereRad * Math.sin(phi) * Math.cos(theta);
				y0 = sphereRad * Math.sin(phi) * Math.sin(theta);
				z0 = sphereRad * Math.cos(phi);

				//We use the addParticle function to add a new particle. The parameters set the position and velocity components.
				//Note that the velocity parameters will cause the particle to initially fly outwards away from the sphere center (after
				//it becomes unstuck).
				var p = addParticle(x0, sphereCenterY + y0, sphereCenterZ + z0, 0.002 * x0, 0.002 * y0, 0.002 * z0);

				//we set some "envelope" parameters which will control the evolving alpha of the particles.
				p.attack = 50;
				p.hold = 50;
				p.decay = 100;
				p.initValue = 0;
				p.holdValue = particleAlpha;
				p.lastValue = 0;

				//the particle will be stuck in one place until this time has elapsed:
				p.stuckTime = 90 + Math.random() * 20;

				p.accelX = 0;
				p.accelY = gravity;
				p.accelZ = 0;
			}
		}

		//update viewing angle
		turnAngle = (turnAngle + turnSpeed) % (2 * Math.PI);
		sinAngle = Math.sin(turnAngle);
		cosAngle = Math.cos(turnAngle);

		//background fill
		context.fillStyle = "#000000";
		context.fillRect(0, 0, displayWidth, displayHeight);

		//update and draw particles
		p = particleList.first;
		while (p != null) {
			//before list is altered record next particle
			nextParticle = p.next;

			//update age
			p.age++;

			//if the particle is past its "stuck" time, it will begin to move.
			if (p.age > p.stuckTime) {
				p.velX += p.accelX + randAccelX * (Math.random() * 2 - 1);
				p.velY += p.accelY + randAccelY * (Math.random() * 2 - 1);
				p.velZ += p.accelZ + randAccelZ * (Math.random() * 2 - 1);

				p.x += p.velX;
				p.y += p.velY;
				p.z += p.velZ;
			}

			/*
			We are doing two things here to calculate display coordinates.
			The whole display is being rotated around a vertical axis, so we first calculate rotated coordinates for
			x and z (but the y coordinate will not change).
			Then, we take the new coordinates (rotX, y, rotZ), and project these onto the 2D view plane.
			*/
			rotX = cosAngle * p.x + sinAngle * (p.z - sphereCenterZ);
			rotZ = -sinAngle * p.x + cosAngle * (p.z - sphereCenterZ) + sphereCenterZ;
			m = radius_sp * fLen / (fLen - rotZ);
			p.projX = rotX * m + projCenterX;
			p.projY = p.y * m + projCenterY;

			//update alpha according to envelope parameters.
			if (p.age < p.attack + p.hold + p.decay) {
				if (p.age < p.attack) {
					p.alpha = (p.holdValue - p.initValue) / p.attack * p.age + p.initValue;
				}
				else if (p.age < p.attack + p.hold) {
					p.alpha = p.holdValue;
				}
				else if (p.age < p.attack + p.hold + p.decay) {
					p.alpha = (p.lastValue - p.holdValue) / p.decay * (p.age - p.attack - p.hold) + p.holdValue;
				}
			}
			else {
				p.dead = true;
			}

			//see if the particle is still within the viewable range.
			if ((p.projX > displayWidth) || (p.projX < 0) || (p.projY < 0) || (p.projY > displayHeight) || (rotZ > zMax)) {
				outsideTest = true;
			}
			else {
				outsideTest = false;
			}

			if (outsideTest || p.dead) {
				recycle(p);
			}

			else {
				//depth-dependent darkening
				depthAlphaFactor = (1 - rotZ / zeroAlphaDepth);
				depthAlphaFactor = (depthAlphaFactor > 1) ? 1 : ((depthAlphaFactor < 0) ? 0 : depthAlphaFactor);
				context.fillStyle = rgbString + depthAlphaFactor * p.alpha + ")";

				//draw
				context.beginPath();
				context.arc(p.projX, p.projY, m * particleRad, 0, 2 * Math.PI, false);
				context.closePath();
				context.fill();
			}

			p = nextParticle;
		}
	}

	function addParticle(x0, y0, z0, vx0, vy0, vz0) {
		var newParticle;
		var color;

		//check recycle bin for available drop:
		if (recycleBin.first != null) {
			newParticle = recycleBin.first;
			//remove from bin
			if (newParticle.next != null) {
				recycleBin.first = newParticle.next;
				newParticle.next.prev = null;
			}
			else {
				recycleBin.first = null;
			}
		}
		//if the recycle bin is empty, create a new particle (a new ampty object):
		else {
			newParticle = {};
		}

		//add to beginning of particle list
		if (particleList.first == null) {
			particleList.first = newParticle;
			newParticle.prev = null;
			newParticle.next = null;
		}
		else {
			newParticle.next = particleList.first;
			particleList.first.prev = newParticle;
			particleList.first = newParticle;
			newParticle.prev = null;
		}

		//initialize
		newParticle.x = x0;
		newParticle.y = y0;
		newParticle.z = z0;
		newParticle.velX = vx0;
		newParticle.velY = vy0;
		newParticle.velZ = vz0;
		newParticle.age = 0;
		newParticle.dead = false;
		if (Math.random() < 0.5) {
			newParticle.right = true;
		}
		else {
			newParticle.right = false;
		}
		return newParticle;
	}

	function recycle(p) {
		//remove from particleList
		if (particleList.first == p) {
			if (p.next != null) {
				p.next.prev = null;
				particleList.first = p.next;
			}
			else {
				particleList.first = null;
			}
		}
		else {
			if (p.next == null) {
				p.prev.next = null;
			}
			else {
				p.prev.next = p.next;
				p.next.prev = p.prev;
			}
		}
		//add to recycle bin
		if (recycleBin.first == null) {
			recycleBin.first = p;
			p.prev = null;
			p.next = null;
		}
		else {
			p.next = recycleBin.first;
			recycleBin.first.prev = p;
			recycleBin.first = p;
			p.prev = null;
		}
	}
}


$(function () {
	$("#slider-range").slider({
		range: false,
		min: 20,
		max: 500,
		value: 280,
		slide: function (event, ui) {
			console.log(ui.value);
			sphereRad = ui.value;
		}
	});
});

$(function () {
	$("#slider-test").slider({
		range: false,
		min: 1.0,
		max: 2.0,
		value: 1,
		step: 0.01,
		slide: function (event, ui) {
			radius_sp = ui.value;
		}
	});
});

 



// -------------------------------


// function addSystemCommand() {
//     const keyword = document.getElementById('syskey').value;
//     const path = document.getElementById('syspath').value;

   
//     if (keyword && path) {
//         const table = document.getElementById('system_commands');
//         const rowCount = table.rows.length + 1;
//         const row = `<tr><td>${rowCount}</td><td>${keyword}</td><td>${path}</td><td><button class='btn btn-danger btn-sm' onclick='deleteRow(this)'>Delete</button></td></tr>`;
//         table.innerHTML += row;
//         document.getElementById('syskey').value = '';
//         document.getElementById('syspath').value = '';
//     }
// }

// function addWebCommand() {
//     const keyword = document.getElementById('webKeyword').value;
//     const url = document.getElementById('webUrl').value;
//     if (keyword && url) {
//         const table = document.getElementById('webCommands');
//         const rowCount = table.rows.length + 1;
//         const row = `<tr><td>${rowCount}</td><td>${keyword}</td><td>${url}</td><td><button class='btn btn-danger btn-sm' onclick='deleteRow(this)'>Delete</button></td></tr>`;
//         table.innerHTML += row;
//         document.getElementById('webKeyword').value = '';
//         document.getElementById('webUrl').value = '';
//     }
// }

// function deleteRow(btn) {
//     const row = btn.parentNode.parentNode;
//     row.parentNode.removeChild(row);
// }


function addSystemCommand(event) {
    event.preventDefault(); // Form submit ka default behavior rok diya

    const keyword = document.getElementById('syskey').value;
    const path = document.getElementById('syspath').value;

    if (keyword && path) {
        const data = {
            name: keyword,
            path: path
        };

        fetch('http://localhost:5000/add_system_command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            alert(result.message); // Backend ka response dikhaya
            if (result.message === 'Command added successfully!') {
                const table = document.getElementById('systemCommands');
                const rowCount = table.rows.length + 1;
                const row = `<tr><td>${rowCount}</td><td>${keyword}</td><td>${path}</td><td><button id="d1" class='btn btn-danger btn-sm' onclick='deleteRow("d1",event)'>Delete</button></td></tr>`;
                table.innerHTML += row;
            }
            document.getElementById('syskey').value = '';
            document.getElementById('syspath').value = '';
        })
        .catch(error => console.error('Error:', error));
    } else {
        alert('Please fill out both fields!');
    }
}

// Web Command ka JS Code yahan se shuru
function addWebCommand(event) {
    event.preventDefault(); // Form submit ka default behavior rok diya

    const keyword = document.getElementById('webKeyword').value;
    const url = document.getElementById('webUrl').value;

    if (keyword && url) {
        const data = {
            name: keyword, // IMPORTANT: Ensure "name" matches backend expectation
            url: url
        };

        fetch('http://localhost:5000/add_web_command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            alert(result.message);
            if (result.message === 'Web command added successfully!') {
                const table = document.getElementById('webCommands');
                const rowCount = table.rows.length + 1;
                const row = `<tr><td>${rowCount}</td><td>${keyword}</td><td>${url}</td><td><button id="d2" class='btn btn-danger btn-sm' onclick='deleteRow("d2",event)'>Delete</button></td></tr>`;
                table.innerHTML += row;
            }
            document.getElementById('webKeyword').value = '';
            document.getElementById('webUrl').value = '';
        })
        .catch(error => console.error('Error:', error));
    } else {
        alert('Please fill out both fields!');
    }
}


function deleteRow(id, event) {
    event.stopPropagation(); // Form submit ko yahan se rok diya
    document.getElementById(id).closest('tr').remove();
}



// async function deleteSystemCommand(id) {
//     console.log('ID being sent to backend:', id);

//     try {
//         const response = await fetch(`http://127.0.0.1:5000/delete_system_command/${id}`, {
//             method: 'DELETE'
//         });

//         const result = await response.json();
//         alert(result.message);

//         if (result.message === 'System command deleted successfully!') {
//             fetchSystemCommands();
//         }
//     } catch (error) {
//         console.error('Fetch error:', error);
//         alert('Failed to delete command');
//     }
// // }


// function deleteCommand() {
// 	const id = document.getElementById('deleteId').value;

// 	if (!id) {
// 		alert('Please enter an ID!');
// 		return;
// 	}

// 	fetch(`http://127.0.0.1:5000/delete-command/${id}`, {
// 		method: 'DELETE'
// 	})
// 	.then(response => response.json())
// 	.then(data => {
// 		alert(data.message);
// 	})
// 	.catch(error => {
// 		console.error('Error:', error);
// 		alert('Failed to delete record');
// 	});
// }

// document.getElementById("deleteForm").addEventListener("delete",function(event)
// {
// 	event.preventDefault();
// 	let id=document.getElementById("delete_id").value;

// 	fetch("/delete",{
// 		 method : "POST",
// 		 headers: {"Content-Type":"application/json"},
// 		 body : JSON.stringify({id : id})
		
// 	})
// 	.then(response => response.json())
// 	.then(data => alert(data.message))
// 	.catch(error => console.error("Error:", error));
// });

function deleteRecord()
{
	const id = document.getElementById('delete_id').value;

	if (!id) {
		alert('Please enter an ID!');
		return;
	}

	fetch('http://127.0.0.1:5000/delete', {
		method: 'POST',
		headers: {"Content-Type":"application/json"},
		body : JSON.stringify({id : id})
	})
	.then(response => response.json())
	.then(data => {
		alert(data.message);
	})
	.catch(error => {
		console.error('Error:', error);
		alert('Failed to delete record');
	});
}



// fetchSystemCommands();

document.addEventListener("DOMContentLoaded", function () {
	fetchSystemCommands();  // Page load hone par system commands fetch karega
});
  




// greeting function
window.onload = function() {
    let now = new Date();
    let hour = now.getHours();
    
    //Random Titles
    let titles = ["Captain", "Chief", "Boss", "Commander", "Leader", "Sir"];
    let randomTitle = titles[Math.floor(Math.random() * titles.length)]; 

    //Random Questions (User se puchne ke liye)
    let questions = [
        "How can I assist you today?",
        "What can I do for you?",
        "How may I help you?",
        "Need any assistance?",
        "What’s on your mind?",
        "How can I make your day better?"
    ];
    let randomQuestion = questions[Math.floor(Math.random() * questions.length)]; 

    let greeting = "";

    if (hour >= 5 && hour < 11) {
        greeting = `Good Morning, ${randomTitle}! ${randomQuestion}`;
    } else if (hour >= 11 && hour < 17) {
        greeting = `Good Afternoon, ${randomTitle}! ${randomQuestion}`;
    } else if (hour >= 17 && hour < 21) {
        greeting = `Good Evening, ${randomTitle}! ${randomQuestion}`;
    } else {
        greeting = `Hello, ${randomTitle}! ${randomQuestion}`;
    }

    //Greeting ko UI pe update karega
    document.querySelector(".text-light").innerText = greeting;  

    //Jarvis ko bolne ka feature (Enthusiastic Speech)
    let speech = new SpeechSynthesisUtterance(greeting);
    speech.volume = 1;   // 0 to 1 (1 = Full Volume)
    speech.rate = 1.2;   // 0.1 to 10 (1 = Normal, 1.2 = Little Faster for energy)
    speech.pitch = 1.5;  // 0 to 2 (1 = Normal, 1.5 = Slightly High-Pitched for enthusiasm)
    
    window.speechSynthesis.speak(speech);
};







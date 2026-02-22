let machines=["Packing_Unit_01","Robotic_Arm_02","Conveyor_System_03"];
let container=document.getElementById("machineContainer");

machines.forEach(machine=>{
container.innerHTML+=`
<div class="card">
<h3>${machine}</h3>

<input id="${machine}_air" placeholder="Air Temp">
<input id="${machine}_process" placeholder="Process Temp">
<input id="${machine}_rot" placeholder="Rot Speed">
<input id="${machine}_torque" placeholder="Torque">
<input id="${machine}_wear" placeholder="Tool Wear">

<button onclick="manualPredict('${machine}')">RUN ANALYSIS</button>

<div class="progress-container">
<div id="${machine}_bar" class="progress-bar"></div>
</div>

<div id="${machine}_percent">0%</div>
<div id="${machine}_status">Monitoring...</div>

<div id="${machine}_live">Live Auto Mode Active...</div>
</div>`;
});

function manualPredict(machine){
let air=document.getElementById(machine+"_air").value;
let process=document.getElementById(machine+"_process").value;
let rot=document.getElementById(machine+"_rot").value;
let torque=document.getElementById(machine+"_torque").value;
let wear=document.getElementById(machine+"_wear").value;

fetch("/manual_predict",{
method:"POST",
headers:{"Content-Type":"application/x-www-form-urlencoded"},
body:
"machine_id="+machine+
"&air_temp="+air+
"&process_temp="+process+
"&rot_speed="+rot+
"&torque="+torque+
"&tool_wear="+wear
})
.then(res=>res.json())
.then(data=>{
document.getElementById(machine+"_bar").style.width=data.probability+"%";
document.getElementById(machine+"_percent").innerHTML=data.probability+"%";
document.getElementById(machine+"_status").innerHTML=data.status;
});
}

setInterval(()=>{
machines.forEach(machine=>{
fetch("/auto_predict/"+machine)
.then(res=>res.json())
.then(data=>{
document.getElementById(machine+"_bar").style.width=data.probability+"%";
document.getElementById(machine+"_percent").innerHTML=data.probability+"%";
document.getElementById(machine+"_status").innerHTML=data.status;

document.getElementById(machine+"_live").innerHTML=
"Air Temp: "+data.air_temp+"<br>"+
"Process Temp: "+data.process_temp+"<br>"+
"Rot Speed: "+data.rot_speed+"<br>"+
"Torque: "+data.torque+"<br>"+
"Tool Wear: "+data.tool_wear;
});
});
},3000);
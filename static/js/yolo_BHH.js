
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM đã được tải xong!");
    document.querySelectorAll('.source-radio').forEach(radio => {
        radio.addEventListener('change', handleSourceChange);
    });


    function handleSourceChange(event) {
        const detailsDiv = document.getElementById('source-details');
        detailsDiv.innerHTML = ''; 

        switch (event.target.value) {
            case 'image':
                reset_scr_rt();
                handleImageUpload(detailsDiv); 
                break;
            case 'video':
                reset_scr_rt();
                handleVideoUpload(detailsDiv);
                break;
            case 'realtime':
                reset_scr_rt();
                handleRealtimeConfig(detailsDiv); 
                break;
            default:
                break;
        }
    }


   function handleImageUpload(container) {
    container.innerHTML = `
        <input type="file" accept="image/*" class="input-field" id="imageUpload">
    `; 
    const imageUpload = document.getElementById('imageUpload');
    imageUpload.addEventListener('change', previewImage);
}

	function previewImage(event) {
    const file = event.target.files[0];
    const displayContainer = document.querySelector('.source_NB'); 
    displayContainer.innerHTML = ''; 

    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = document.createElement('img'); 
            img.src = e.target.result;
            img.alt = 'Image Preview';
            img.style.maxWidth = '100%'; 
            img.style.maxHeight = '100%'; 
            displayContainer.appendChild(img); 
            sendImageFlask(file)
        };
        reader.readAsDataURL(file);
    }
}
async function sendImageFlask(file){
	const formData = new FormData();
	formData.append('file',file);
	
	try{
		const response = await fetch('/detect_image',{
			method:"POST",
			body:formData
		});
		const data =await response.json();
		if(data.result_image){
			const resultContainer = document.querySelector('.result_NB');
			if(resultContainer){
				resultContainer.innerHTML='';
				const resultImg = document.createElement('img');
				resultImg.src = data.result_image;
				resultImg.alt = "Detected Image";
				resultImg.style.maxHeight='100%';
				resultImg.style.maxWidth='100%';
				resultContainer.appendChild(resultImg);
			}else{
				console.error('result container not found');
			}
		}else{
			console.error('error from server',data.error);
		}



        ppx = document.querySelector('.Describe_list');
        ppx.innerHTML= '';
        const listCount = data.list_count;
        let sum = 0;
        for (const [key, value] of Object.entries(listCount)) {
            const newLi = document.createElement('li');
            newLi.textContent = `${key}: ${value}`;
            sum += value
            ppx.appendChild(newLi);
        }
        const sum_tong = document.createElement('li');
        sum_tong.textContent ="Tong So Doi Tuong: "+ sum;
        ppx.appendChild(sum_tong);

        const dataCaption = data.image_caption;
        const image_cap = document.createElement('li');
        image_cap.textContent = dataCaption;
        ppx.appendChild(image_cap);

	}catch(error){
		console.error('error sending image to flask ',error);
	}
}


    // Hàm xử lý tải lên video (chưa triển khai)
 function handleVideoUpload(container) {
    container.innerHTML = `
        <input type="file" accept="video/*" class="input-field" id="videoUpload">
    `; 
    const videoUpload = document.getElementById('videoUpload');
    videoUpload.addEventListener('change', previewVideo);
}

function previewVideo(event) {
    const file = event.target.files[0];
    const displayContainer = document.querySelector('.source_NB'); 
    displayContainer.innerHTML = ''; 

    if (file) {
        const url = URL.createObjectURL(file); 
        const video = document.createElement('video'); 
        video.src = url; 
        video.controls = true; 
        video.style.maxWidth = '100%'; 
        video.style.maxHeight = '100%'; 
        displayContainer.appendChild(video); 
        video.load(); 
        video.style.display = 'block'; 
		sendFileToFlask_video(file, '/detect_video');
    } else {
        alert('Vui lòng chọn video phù hợp.');
    }
}
async function sendFileToFlask_video(file, endpoint) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        
        const resultContainer = document.querySelector('.result_NB');
        resultContainer.innerHTML = '';
        if (data.result_video) {
            const resultVideo = document.createElement('video');
            resultVideo.src = data.result_video;
            resultVideo.controls = true;
            console.log("Đặt nguồn video đã xử lý thành:", resultVideo.src);
            resultVideo.style.maxHeight = '100%';
            resultVideo.style.maxWidth = '100%';
            resultContainer.appendChild(resultVideo);

        } else {
            console.error('Error from server:', data.error);
        }
    } catch (error) {
        console.error('Error sending file to Flask:', error);
    }
}

    // Hàm cấu hình real-time (chưa triển khai)
function handleRealtimeConfig(container) {
	const sourceNB = document.querySelector('.source_NB');
	const resultNB = document.querySelector('.result_NB');
	
    const sourceImg = document.createElement('img');
    sourceImg.setAttribute('id', 'sourceVideo');
    sourceImg.setAttribute('width', '400');
    sourceImg.setAttribute('height', '300');
    sourceImg.src = '/source_feed';
    sourceImg.style.display = 'block';
	sourceImg.onerror = () => console.error("Error loading source_feed stream");
    sourceImg.onload = () => console.log("Source_feed stream loaded");
    sourceNB.appendChild(sourceImg);

    const resultImg = document.createElement('img');
    resultImg.setAttribute('id', 'resultVideo');
    resultImg.setAttribute('width', '400');
    resultImg.setAttribute('height', '300');
    resultImg.src = '/video_feed';
    resultImg.style.display = 'block';
	resultImg.onerror = () => console.error("Error loading video_feed stream");
    resultImg.onload = () => console.log("Video_feed stream loaded");
    resultNB.appendChild(resultImg);

    updateObjectCounts();
    setInterval(updateObjectCounts, 1000);
}
async function updateObjectCounts(){
    try {
        const response = await fetch('/get_object_count_realtime');
        let sum =0;
        const data = await response.json();
        const ppx = document.querySelector(".Describe_list");
        ppx.innerHTML = "";
        for (const [key, value] of Object.entries(data)) {
            const newLi = document.createElement('li');
            newLi.textContent = `${key}: ${value}`;
            sum += value;
            ppx.appendChild(newLi);
        }
        const sum_tong = document.createElement('li');
        sum_tong.textContent ="Tong So Doi Tuong: "+ sum;
        ppx.appendChild(sum_tong);

        updateCaptionRealTime(ppx);
    } catch (error) {
        console.error(e);
        // document.querySelector("..Describe_list").innerHTML = '<p> e </p>'
    }
}
async function updateCaptionRealTime(param){
    try {
        const response = await fetch('/describe_topic');
        const data =  await response.json();
        const caption_img = document.createElement('li');
        caption_img.textContent = data;
        param.appendChild(caption_img);
    } catch (error) {
        console.error(e);
    }
}
function reset_scr_rt(){
    const sourceNB = document.querySelector('.source_NB');
	const resultNB = document.querySelector('.result_NB');
    sourceNB.innerHTML='';
    resultNB.innerHTML='';
}


});
const clearButton =document.getElementsByClassName("Clear_");
clearButton[0].onclick = function(){
	location.reload();
};
function stopWebcam() {
    fetch('/stop', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        window.location.reload();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to stop webcam');
    });
}
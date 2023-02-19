<template>
    <div>

        <!-- component -->
        <label class="mainButton">
            <span><i class="fa-solid fa-cloud-arrow-up"></i> File</span>
            <input accept="audio/*, video/*" type="file" class="hidden" @change="onFileUpload">
        </label>

        <label @click="toggleURL" id="youtubeSelect" class="mainButton">
            <span><i class="fa-brands fa-youtube"></i> YouTube</span>
        </label>

        <label @click="submitJob" id="transcribe" class="mainButton2 ">
            <span><i class="fa-regular fa-comment"></i> Transcribe</span>
        </label>
        <div v-if="showURL" class="">
            <input ref="youTubeURL" id="youTubeURL" class="url" type="text" size="40" placeholder="Paste the YouTube URL here">
        </div>
        <div v-if="FILE" class="">
            <span ref="selectedFileName" class="selectedFileName">Selected file: {{ FILE.name }} </span>
        </div>
    </div>

</template>

<script>
import axios from "axios";
export default {
    data() {
        return {
            showURL: false,
            FILE: null,
        }
    },
    methods: {
        onFileUpload (event) {
            this.FILE = event.target.files[0]
            this.showURL = false
        },
        toggleURL() {
            this.showURL = !this.showURL
            this.FILE = null
        },
        submitJob() {
            const formData = new FormData()
            if ( this.showURL )
            {
                // submit youtube job
                const url = this.$refs.youTubeURL.value
                formData.append('youtubeURL', url);
            } else {
                // submit file job
                formData.append('file', $('#fileSelect')[0].files[0]);
            }

            axios.post('http://localhost:8081/addItem', formData, {
            }).then((res) => {
                console.log(res)
            })

        }
    }
}
</script>

<style>

.hidden {
    display: none;
}

.mainButton2 {
    -webkit-user-select: none; /* Safari */
    -ms-user-select: none; /* IE 10 and IE 11 */
    user-select: none; /* Standard syntax */

    display: inline-block;
    background-color: #3D5164;
    color: white;
    font-weight: 600;
    border-radius: 5px;
    padding: 10px 20px;
    margin: 10px 0 20px 20px ;
}

.mainButton {
    -webkit-user-select: none; /* Safari */
    -ms-user-select: none; /* IE 10 and IE 11 */
    user-select: none; /* Standard syntax */

    display: inline-block;
    background-color: #3D5164;
    color: white;
    font-weight: 600;
    border-radius: 5px;
    padding: 10px 20px;
    margin: 20px 5px;
}

.mainButton:hover,
.mainButton2:hover {
    background-color: #212d37;
    color: white;
}

.url {
    text-align: center;
    justify-content: center;
    line-height: 2em;;
}

.selectedFileName {
    text-align: center;
    justify-content: center;
    line-height: 2em;;
    color: #555;
    padding: 10px 6px;
    margin-bottom: 20px;
    border-radius: 10px;
    display: inline-flex;
}

input {
    text-align: center;
    justify-content: center;
    font-size: 18px;
    padding: 10px 6px;
    margin-bottom: 20px;
    box-sizing: border-box;
    border: none;
    border-bottom: 1px solid #ddd;
    color: #555;
    width: 400px;
}

</style>
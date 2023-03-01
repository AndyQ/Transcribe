<template>
    <div class="ViewTranscription">
        <div style="height:20px;"></div>
        <div class="header text-center">
            <div class="col">
                <h1 class="txt-dark">{{title}}</h1>
            </div>
        </div>
        <div style="height:20px;"></div>

        <div class="row">
            <div class="videoDiv">
                <div class="video-container">
                    <div id="yt-player"></div>
                </div>
            </div>
        </div>

        <div ref="transcription" class="transcription">
            <div v-for="item in transcription" :key="item.time" class="segment" ref="segments" style="font-weight: normal;">
                <p>
                    {{ format_millis(item.start) }}
                    <a @click="pause">◼</a>
                    &nbsp;
                    <a @click="seek( format_secs(item.start) );">►</a>
                    {{item.text}}
                </p>
            </div>
        </div>
    </div>

</template>

<script>
import { markRaw } from '@vue/reactivity';

import LayoutPlayer from '../layouts/LayoutPlayer.vue';

export default {
    name: 'ViewTranscription',
    components: {
        LayoutPlayer
    },

    data() {
        return {
            title: "",
            transcription: [],
            file: null,
            player: null,
            iframeWindow : null,
            lastTimeUpdate : 0,
            lastBold : null,
        }
    },
    methods: {
        
        format_millis(millis) {
            var seconds = parseInt(millis/1000)%60
            var minutes = parseInt(millis/(1000*60))%60
            var hours = parseInt(millis/(1000*60*60))%24

            seconds = (seconds >= 10) ? seconds : "0" + seconds;
            minutes = (minutes >= 10) ? minutes : "0" + minutes;
            hours = (hours >= 10) ? hours : "0" + hours;

            return `${hours}:${minutes}:${seconds}`
        },
        format_secs(millis) {
            return millis / 1000
        },
        setupPlayer() {
            console.log( "Setting up....")
            var tag = document.createElement("script");

            tag.src = "https://www.youtube.com/iframe_api";
            var firstScriptTag = document.getElementsByTagName("script")[0];
            if ( firstScriptTag == null || firstScriptTag.src != tag.src ) {
                firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
            }
        },

        initYoutube() {
            const _ = this;

            console.log("initYoutube");
            this.player = new YT.Player("yt-player", {
                width: 600,
                height: 400,
                videoId: this.file,
                events: {
                onReady: _.onPlayerReady,
                onStateChange: _.onPlayerStateChange
                }
            });
            window.iframeWindow = this.player.getIframe().contentWindow;

        },
        onPlayerReady(evt) {
            console.log("Player ready");
            // evt.target.playVideo();
        },
        onPlayerStateChange(evt) {
            console.log("Player state changed", evt);
        },
        handleMessage(event) {
            var data = JSON.parse(event.data);

            // The "infoDelivery" event is used by YT to transmit any
            // kind of information change in the player,
            // such as the current time or a playback quality change.
            if (
                data.event === "infoDelivery" &&
                data.info &&
                data.info.currentTime
            ) {
                var time = data.info.currentTime;
                for (let index in this.transcription ) {
                    const item = this.transcription[index]

                
                    if(time < this.format_secs(item.end) ) {

                        const segment = this.$refs.segments[index]
                        if ( segment != this.lastBold ) {
                            if(this.lastBold) {
                                this.lastBold.style.fontWeight = "normal";
                            }

                            if (!this.checkIfInView(segment)) {
                                var parentDiv =  this.$refs.transcription
                                console.log( "item not in view!")

                                const itemRelativePos = (segment.offsetTop-parentDiv.offsetTop)-parentDiv.scrollTop

                                parentDiv.scrollTop += itemRelativePos - (parentDiv.offsetHeight - (segment.offsetHeight*3))
                            }
                            this.lastBold = segment;
                            this.lastBold.style.fontWeight = "bold"; 
                            console.log( `Set item {index} to bold!`)
                        }                    

                        return;
                    }
                }
            }
        },
        checkIfInView2(id){
            const element = this.$refs.segments[id]
            if ( !this.checkIfInView(element) ) {
                console.log( "item not in view!")
                var parentDiv =  this.$refs.transcription

                console.log( "element.offsetTop " + element.offsetTop)
                console.log( "element.offsetHeight " + element.offsetHeight)
                console.log( "parentDiv.offsetTop " + parentDiv.offsetTop)
                console.log( "parentDiv.offsetHeight " + parentDiv.offsetHeight)
                console.log( "parentDiv.scrollTop  " + parentDiv.scrollTop)


            } else {
                console.log( "item in view!")
            }

        },
        checkIfInView(element){
            var parentDiv =  this.$refs.transcription

            const itemRelativePos = (element.offsetTop-parentDiv.offsetTop)-parentDiv.scrollTop
            if ( itemRelativePos > parentDiv.offsetHeight - (element.offsetHeight*3) ) {
                return false;
            }
            return true;
        },
        pause() {
            if(this.player) {
                this.player.pauseVideo();
            }
        },
        seek(sec) {
            if ( this.player ) {
                const seconds = sec;
                this.player.seekTo(seconds, true);
                this.player.playVideo()
            }
        },
    },
    
    mounted() {
        window.vueapp=this;

        console.log( "Mounted!")
        fetch('http://localhost:8081/getItem/' + this.$route.params.id)
            .then (res => res.json() )
            .then(data => {
            
                if ( this.file == null ) {
                    this.title = data.title
                    this.transcription = data.transcription
                    this.file = data.file
                    this.setupPlayer()
                }
            })
            .catch (err => console.log( err.message ))
    },
    unmounted() {
        // Remove all scripts except the app,js script
        var scripts = document.getElementsByTagName("script")
        for (let i = scripts.length-1; i>= 0 ; i--) {
            if ( !scripts[i].src.includes('app.js')) {
                scripts[i].parentNode.removeChild(scripts[i]);
            }
        }

    },
    created() {
        console.log( )
        this.$emit('update:layout', markRaw(LayoutPlayer));
    },
}

window.onYouTubeIframeAPIReady = () => {
    console.log("onYouTubeIframeAPIReady");
    window.vueapp.initYoutube();    
};

window.addEventListener("message", function(event) {
    if (event.source === window.iframeWindow) {
        window.vueapp.handleMessage(event);
    }
});



</script>

<style>


    .ViewTranscription {
        display: flex;
        flex-direction: column;
        max-height: 100vh;       /* body takes whole viewport's height */

    }

    .transcriptionWrapper2 {
        bottom: 100px;
    }

    .transcription {
        flex: 1;
        overflow: auto;
        text-align: left;
        margin: 10px 50px 0px 50px;
    }

    .videoDiv {
        max-width: 1024px;
        margin-left: auto;
        margin-right: auto;
    }

    .video-container {
        position: relative;
        padding-bottom: 56.25%;
        margin-left: 10px;
        margin-right: 10px;
    }

    .video-container iframe {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
    }

</style>
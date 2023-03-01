<template>
    <div class="Home">
        <div ref="transcribe" class="transcribe">
            <Transcribe />
        </div>

        <div ref="title" class="title">
            <div class="queue">
                <h1>Waiting</h1>
            </div>
            <div class="queue">
                <h1>Processing</h1>
            </div>
            <div class="queue">
                <h1>Complete</h1>
            </div>
        </div>

        <div ref="queues" class="queues">
            <div class="queue">
                <Queue type="waiting" :data="waiting"/>
            </div>
            <div class="queue">
                <Queue type="processing" :data="processing"/>
            </div>
            <div class="queue">
                <Queue type="completed" :data="completed"/>
            </div>
        </div>
    </div>
</template>

<script>
import LayoutDefault from '../layouts/LayoutDefault.vue';
import Transcribe from '../components/Transcribe.vue';
import Queue from '../components/Queue.vue';
import { markRaw } from '@vue/reactivity';

export default {
    name: 'Home',
    components: {
        LayoutDefault, Transcribe, Queue
    },
    data() {
        return {
            waiting: [],
            processing: [],
            completed: [],
        }
    },
    methods: {
        updateViews() {
            var titles = this.$refs.title;
            var queues = this.$refs.queues;
            
            // get header height
            var headerTop = titles.offsetTop;
            var headerHeight = titles.offsetHeight;
            
            // get header2 height
            var header2Top = headerTop + headerHeight;
            
            // set container top margin to header height
            queues.style.top = `${header2Top}px`
        },
        updateQueues() {
            fetch('http://localhost:8081/getQueueDetails')
                .then (res => res.json() )
                .then(data => {
                    let serviceData = data
                    console.log( "sd - " + JSON.stringify(serviceData))
                    this.waiting = serviceData.waiting
                    this.processing = serviceData.inprogress
                    this.completed = serviceData.done
                })
                .catch (err => console.log( err.message ))
        }
    },
    mounted() {
        this.updateViews()

        this.updateQueues()
        setInterval(this.updateQueues,1000);

        // get data
    },
    created() {
        this.$emit('update:layout', markRaw(LayoutDefault));
    },
};
</script>

<style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    
    .transcribe {
      height: 150px;
    }

    .title {
      --column-width : calc(33.33% - (var(--margin) / var(--column-count)));
      --column-count :3; 
      --margin : 20px;

      width: calc(100% - (2 * var(--margin)));
      margin-left: var(--margin);
       display:flex; 
       flex-direction : row; 
       justify-content : space-between; 
    }   

    .queues {
        position: absolute;
        bottom: 80px; /* same as footer height */
        width: 100%; 

        --column-width : calc(33.33% - (var(--margin) / var(--column-count)));
        --column-count :3; 
        --margin : 20px;

        width: calc(100% - (2 * var(--margin)));
        margin-left: var(--margin);
                
        display:flex; 
        flex-direction : row; 
        justify-content : space-between; 
       
     }
     
     .queue {
        width: calc(100% - (2 * var(--margin)));
        overflow-y : auto; 
        margin-left: 20px;
        margin-right: 20px;
        text-align: left;
    }

</style>
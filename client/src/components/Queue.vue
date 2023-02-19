<template>
    <div class="items" v-for="item in data" :key="item.id">
        <span class="item">
            
            <div v-if="type == 'completed'">
                <i @click="deleteItem(item.id)" v-if="type == 'completed'" class="deleteItem fa-solid fa-trash"></i> 
                <router-link :to="{ name: 'viewTranscription', params: { id : item.id } }" target="_blank">{{ item.title }}</router-link>
            </div>
            <div v-else>
                <i @click="deleteItem(item.id)" v-if="type == 'completed'" class="deleteItem fa-solid fa-trash"></i> 
                <span>{{item.title}}</span>
            </div>

        </span>

  </div>
</template>

<script>
import { ref } from '@vue/reactivity'
import axios from "axios";

export default {
    props: ['type', "data"],
    setup(props) {
        const items = ref([])

        const deleteItem = (id) => {
            console.log(id)

            const formData = new FormData()
            formData.append('id', id);
            axios.post('http://localhost:8081/deleteItem', formData, {
            }).then((res) => {
                console.log(res)
            })
        }

        return { items, deleteItem }
    }
}
</script>

<style>
.item {
    color: #3D5164;
    font-weight: normal;
    font-size: 1.2em;
    line-height: 2em;
}

</style>
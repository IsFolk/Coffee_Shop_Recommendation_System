<template>
  <!--Clock icons created by Freepik - Flaticon -->
  <div>
    <div>
      <div class="store-pane">
        <!-- 搜尋欄 -->
        <div class="central-container">
          <input
            id="search-input"
            v-model="searchInput"
            placeholder="想找什麼咖啡廳ㄋ"
            @input="handleInput"
          />

          <button
            @click="search_word2vec"
          >CKIP自定義辭典標籤</button>

          <button
            style="--c:#E95A49"
            @click="search_sentiment"
          >JIEBA斷詞情感分析</button>
        </div>
        <div class="central-container">
          <p class="label" v-for="label in query_label" :key="label.id">
            #{{ label }}
          </p>
        </div>
      </div>

      <!-- 包含所有搜尋到的店家 -->
      <div class="store-pane">

        <!-- 包含單間店家的所有資訊 -->
        <div class="store-container" v-for="store in stores" :key="store.id">

          <!-- 店家圖片，如果沒有跑出來會跑loading的gif -->
          <div class="picture-container">
            <img
              :src="store.img"
              :alt="store.name"
              @error="handleImageError"
            />
          </div>

          <!-- 店家文字資訊(店名、評分、label) -->
          <div class="store-info-container">
            <div class="store-name">
              <p>{{ store.name }}</p>
            </div>
            <div class="rating-container">
              <p class="rating">評分 {{ store.star }} 分</p>
            </div>

            <!-- 各店家的label -->
            <div class="label-container">
              <p class="label" v-for="label in store.labels" :key="label.id">
                #{{ label }}
              </p>
            </div>
          </div>

          <!-- 地圖、營業時間連結 -->
          <div class="tool-bar-container">
            <input
              type="image"
              class="icon-btn"
              @click="openMap(store)"
              :src="mapIcon"
            />
            <input
              type="image"
              class="icon-btn"
              @click="togglePopup(store.id)"
              :src="clockIcon"
            />
          </div>

          <!-- 營業時間的popup框改到這裡 -->
          <div class="popup-container">
            <div
              v-if="showPopup[store.id]"
              class="popup"
              :style="{ display: showPopup[store.id] ? 'block' : 'none' }"
            >
              <span class="close" @click="togglePopup(store.id)">&times;</span>
              <p>{{ store.time }}</p>
              <p></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from "@vue/reactivity";
import axios from "axios";
import { computed, onMounted } from "vue";
import searchIcon from '..\\assets\\search_icon.png';
import loadingIcon from '..\\assets\\loading.gif'
import mapIcon from '..\\assets\\map_icon.png'
import clockIcon from '..\\assets\\clock.png'
import deepLIcon from '..\\assets\\deep-learning.png'



export default {
  data() {
    return {
      searchInput: "",
      stores: [],
      query_label: [],
      popupState: {}, // 添加這一行,
      showPopup: {},
      searchIcon: searchIcon,
      loadingIcon: loadingIcon,
      mapIcon: mapIcon,
      clockIcon: clockIcon,
      deepLIcon: deepLIcon
    };
  },
  methods: {
    handleImageError(event) {
      console.log("handleImageError called");
      event.preventDefault();
      event.target.src = this.loadingIcon;
    },
    togglePopup(storeid) {
      // console.log(storeid)
      // 切換特定 store 的浮框狀態
      this.showPopup[storeid] = !this.showPopup[storeid];
      // console.log(this.showPopup)

      // 在點擊事件中將 store.time 中的分號 ";" 替換為換行符號 "\n"
      if (this.stores.find((store) => store.id === storeid)) {
        const clickedStore = this.stores.find((store) => store.id === storeid);
        if (clickedStore.time) {
          clickedStore.time = clickedStore.time.replace(/;/g, "\n");
        }
      }
    },
    openMap(store) {
      window.open(store.link, "_blank", "noreferrer");
    },
    handleInput() {},

    search_word2vec() {
      var searchString = this.searchInput;
      // console.log(searchString);
      const port = 8000; // 指定服务器端口号
      const url = `http://localhost:${port}/query_word2vec/${searchString}/`;
      // const url = "http://localhost:5173/src/assets/trans_storeinfo.json";
      axios.get(url).then((response) => {
        var data = response.data.stores;
        var modifiedData = data.map((item) => ({
          link: item.link,
          id: item.id,
          name: item.name,
          time: item.time,
          phone: item.phone,
          img: item.img,
          website: item.website,
          star: item.star,
          review_num: item.review_num,
          labels: item.labels,
        }));
        this.stores = modifiedData;
        this.query_label = response.data.query_label;
        modifiedData.forEach((element) => {
          this.showPopup[element.id] = false;
        });
      });
    },

    search_sentiment() {
      var searchString = this.searchInput;
      // console.log(searchString);
      const port = 8000; // 指定服务器端口号
      const url = `http://localhost:${port}/query_sentiment/${searchString}/`;
      // const url = "http://localhost:5173/src/assets/trans_storeinfo.json";
      axios.get(url).then((response) => {
        var data = response.data.stores;
        var modifiedData = data.map((item) => ({
          link: item.link,
          id: item.id,
          name: item.name,
          time: item.time,
          phone: item.phone,
          img: item.img,
          website: item.website,
          star: item.star,
          review_num: item.review_num,
          labels: item.labels,
        }));
        this.stores = modifiedData;
        this.query_label = response.data.query_label;
        modifiedData.forEach((element) => {
          this.showPopup[element.id] = false;
        });
      });
    },



  },
};
</script>

<style scoped>
.store-pane {
  padding-top: 40px;
}

/* 搜尋欄 */
#search-input {
  width: 400px;

  border-radius: 50px;
  border-color: #ccc;
  text-align: center;
}

/* icon大小和地圖、時鐘的排版 */
.icon-btn {
  height: 50px;
  width: 50px;
  margin-inline: 10px;
}

.tool-bar-container {
  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
}

/* 一個店家的所有資訊(含圖片和資訊、連結) */
.store-container {
  display: flex;
  flex-direction: row;
  justify-content: start;
  /* align-items: center; */
  position: relative;
  height: min-content;
  width: 700px;
  border-radius: 8px;
  margin: 10px;
  box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.2), 0 4px 8px 0 rgba(0, 0, 0, 0.19);
}

/* 店家圖片相關 */
.picture-container {
  min-height: 140px;
  max-height: 180px;
  width: 200px;
}

img {
  height: 100%;
  max-height: 180;
  width: inherit;
  object-fit: cover;
  object-position: center;
  border-radius: 8px 0px 0px 8px;
  vertical-align: top;
}

/* 店家資訊(文字) */
.store-info-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
  align-items: flex-start;
  margin: 10px 20px;
}

.store-name {
  font-size: 18px;
  color: rgb(1, 78, 78);
  font-weight: bold;
}

/* 橫向排的物件 */
.store-info > div,
.central-container {
  display: flex;
  flex-flow: row wrap;
  justify-content: center;
}

.store-info-container > div > p {
  text-align: left;
  margin: 0;
  padding-inline: 10px;
}

/* label依列排序 */
.label {
  font-size: 14px;
  font-weight: 900;
  color: teal;
  padding-inline: 25px 0px;
}

.label-container {
  display: flex;
  flex-flow: row;
}

/* 昱婷大神做的時間資訊欄 QvQ */
.popup-container {
  position: relative;
}

.popup {
  width: max-content;
  display: none;
  position: absolute;
  /* bottom: 0px; */
  left: 15%;
  transform: translateX(10%);
  padding: 20px;
  background-color: #f1f1f1;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.close {
  position: absolute;
  top: 5px;
  right: 10px;
  font-size: 14px;
  cursor: pointer;
}

.popup p {
  margin: 0;
  white-space: pre-line;
  text-align: left;
}
</style>

<style scoped>

/* CSS */
button {
  --c:  #229091; /* the color*/
  
  box-shadow: 0 0 0 .1em inset var(--c); 
  --_g: linear-gradient(var(--c) 0 0) no-repeat;
  background: 
    var(--_g) calc(var(--_p,0%) - 100%) 0%,
    var(--_g) calc(200% - var(--_p,0%)) 0%,
    var(--_g) calc(var(--_p,0%) - 100%) 100%,
    var(--_g) calc(200% - var(--_p,0%)) 100%;
  background-size: 50.5% calc(var(--_p,0%)/2 + .5%);
  outline-offset: .1em;
  transition: background-size .4s, background-position 0s .4s;
}
button:hover {
  --_p: 100%;
  transition: background-position .4s, background-size 0s;
}
button:active {
  box-shadow: 0 0 9e9q inset #0009; 
  background-color: var(--c);
  color: #fff;
}



body {
  height: 100vh;
  margin: 0;
  display: grid;
  place-content: center;
  grid-auto-flow: column;
  gap: 40px;
  background: #F2DCA2;
}
button {
  font-family: system-ui, sans-serif;
  /* font-size: 3.5rem; */
  cursor: pointer;
  /* padding: .1em .6em; */
  font-weight: bold;  
  border: none;
  font-size: 1rem; /* 调整字体大小 */
  padding: 0.5em 1em; /* 调整内边距 */
  margin: 0; /* 可以调整按钮的外边距 */
}


button img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}
</style>

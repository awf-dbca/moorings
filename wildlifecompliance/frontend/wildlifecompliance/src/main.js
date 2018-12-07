// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import resource from 'vue-resource'
import App from './App'
import router from './router'
import bs from 'bootstrap'
import helpers from '@/utils/helpers'
import hooks from './packages'
import api_endpoints from './api'
require( '../node_modules/bootstrap/dist/css/bootstrap.css' );
//require('../node_modules/eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.min.css')
require( '../node_modules/font-awesome/css/font-awesome.min.css' )

Vue.config.devtools = true;
Vue.config.productionTip = false
Vue.use( resource );

// Add CSRF Token to every request
Vue.http.interceptors.push( function ( request, next ) {
  // modify headers
  if ( request.url != api_endpoints.countries ) {
    request.headers.set( 'X-CSRFToken', helpers.getCookie( 'csrftoken' ) );
  }

  // continue to next interceptor
  next();
} );

Vue.filter('toCurrency', function(value) {
                if (typeof value !== "number") {
                    return value;
                }
                var formatter = new Intl.NumberFormat('en-AU', {
                    style: 'currency',
                    currency: 'AUD',
                    minimumFractionDigits: 2
                });
                return formatter.format(value);
            });

/* eslint-disable no-new */
window.vue = new Vue( {
    el: '#app',
    router,
    template: '<App/>',
    components: {
        App
    },
    computed: {
        wc_version: function (){
            return wc_version;
        }
    },
    methods:{
        setSelectedTabId: function(target) {
            var tab_id = target.href.split('#')[1];
            this.$children[0].$children[0].$children[0].$children[0].$children[0].selected_activity_type_tab_id = parseInt(tab_id);
            return parseInt(tab_id);
        },
    },
})

Vue.config.devtools = true

"use strict";(self.webpackChunkr3f_bathymetry_preview=self.webpackChunkr3f_bathymetry_preview||[]).push([[416],{119:function(e,r,t){t.d(r,{fv:function(){return w}});var n=t(4925),o=t(1413),a=t(2791),i=t(1421),u=t(1255),s=t(3655),c=t(184),l=["url"],f=function(e){var r=e.url,t=(0,n.Z)(e,l),a=(0,s.L)(r).scene;return(0,c.jsx)("primitive",(0,o.Z)({object:a},t))},m=t(6659),v=["urlCoaster","urlsWater","importRotation","orientationSequence"],h=function(e){var r=Object.assign({},e);return(0,c.jsxs)("mesh",(0,o.Z)((0,o.Z)({},r),{},{children:[(0,c.jsx)("boxGeometry",{args:[101.6,12.7,101.6]}),(0,c.jsx)("meshStandardMaterial",{color:"beige"})]}))},w=function(e){var r=e.urlCoaster,t=e.urlsWater,s=e.importRotation,l=void 0===s?0:s,w=e.orientationSequence,p=void 0===w?[(new u.Quaternion).setFromAxisAngle(new u.Vector3(0,1,0),0)]:w,d=(0,n.Z)(e,v),b=(new u.Quaternion).copy(p[0]),x=(0,a.useRef)(null),g=(0,m.vO)(),j=function(e){var r=e.getElapsedTime();x.current.position.y+=.01*Math.sin(1*r),x.current.rotation.z+=.01*Math.cos(.5*r),x.current.rotation.y+=.01*Math.cos(.7*r)};return(0,i.y)((function(e){var r=e.clock;if(x.current){var t=p.length-1;if(t<=0)return x.current.setRotationFromQuaternion(b),void j(r);var n=1/t;p.forEach((function(e,o){var a=(o-1)/t;if(!(a<0)&&g.visible(a,n)){var i=p[o-1],u=g.range(a,n);b.slerpQuaternions(i,e,u),x.current.setRotationFromQuaternion(b),j(r)}}))}})),(0,c.jsx)("group",(0,o.Z)((0,o.Z)({ref:x},d),{},{children:(0,c.jsxs)(a.Suspense,{fallback:(0,c.jsx)(h,{}),children:[(0,c.jsx)(f,{url:r,"rotation-y":l}),t.map((function(e,r){return(0,c.jsx)(f,{url:e,"rotation-y":l},"water-model-".concat(r))}))]})}))}},3611:function(e,r,t){t.r(r),t.d(r,{CoasterSanFranciscoBay:function(){return c},default:function(){return l}});var n=t(1413),o=t(1255),a=t(119),i=t.p+"static/media/water.18786942057b35054943.glb",u=t.p+"static/media/coaster.7135aff6fdcb41a2403d.glb",s=t(184),c=function(e){var r=Object.assign({},e);return(0,s.jsx)(a.fv,(0,n.Z)({urlCoaster:u,urlsWater:[i],importRotation:Math.PI,orientationSequence:[(new o.Quaternion).setFromAxisAngle(new o.Vector3(0,1,0),0),(new o.Quaternion).setFromEuler(new o.Euler(0,0,Math.PI/2,"ZYX")),(new o.Quaternion).setFromEuler(new o.Euler(Math.PI/2,0,Math.PI/2,"ZYX")),(new o.Quaternion).setFromEuler(new o.Euler(0,Math.PI/2,0,"YXZ")),(new o.Quaternion).setFromAxisAngle(new o.Vector3(0,1,0),0)]},r))},l=c}}]);
//# sourceMappingURL=416.d714650e.chunk.js.map
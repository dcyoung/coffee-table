"use strict";(self.webpackChunkr3f_bathymetry_preview=self.webpackChunkr3f_bathymetry_preview||[]).push([[191],{119:function(t,r,n){n.d(r,{fv:function(){return m}});var e=n(4925),o=n(1413),i=n(2791),a=n(1421),c=n(1255),u=n(3655),s=n(184),f=["url"],l=function(t){var r=t.url,n=(0,e.Z)(t,f),i=(0,u.L)(r).scene;return(0,s.jsx)("primitive",(0,o.Z)({object:i},n))},d=["urls","importRotation","orientation"],b=function(t){var r=Object.assign({},t);return(0,s.jsxs)("mesh",(0,o.Z)((0,o.Z)({},r),{},{children:[(0,s.jsx)("boxGeometry",{args:[101.6,12.7,101.6]}),(0,s.jsx)("meshStandardMaterial",{color:"beige"})]}))},m=function(t){var r=t.urls,n=t.importRotation,u=void 0===n?0:n,f=t.orientation,m=void 0===f?(new c.Quaternion).setFromAxisAngle(new c.Vector3(0,1,0),0):f,p=(0,e.Z)(t,d),v=(0,i.useRef)(null);return(0,a.y)((function(t){var r=t.clock;v.current&&function(t){var r=t.getElapsedTime(),n=5e-4;v.current.position.y+=n*Math.sin(1*r),v.current.rotation.z+=n*Math.cos(.5*r),v.current.rotation.y+=n*Math.cos(.7*r)}(r)})),(0,i.useEffect)((function(){v.current.setRotationFromQuaternion(m)}),[m]),(0,s.jsx)("group",(0,o.Z)((0,o.Z)({ref:v},p),{},{children:(0,s.jsx)(i.Suspense,{fallback:(0,s.jsx)(b,{}),children:r.map((function(t,r){return(0,s.jsx)(l,{url:t,"rotation-y":u},"model-".concat(r))}))})}))}},1933:function(t,r,n){n.r(r),n.d(r,{CoasterSanFranciscoBay:function(){return u},default:function(){return s}});var e=n(1413),o=n(1255),i=n(119),a=n.p+"static/media/water-draco.f7bd0749d9d4b66c71fd.glb",c=n.p+"static/media/coaster-draco.e513bab168cb3f385300.glb",u=function(t){var r=Object.assign({},t);return(0,i.fv)((0,e.Z)({urls:[c,a],importRotation:Math.PI,orientation:(new o.Quaternion).setFromAxisAngle(new o.Vector3(0,1,0),0)},r))},s=u}}]);
//# sourceMappingURL=191.813391f9.chunk.js.map
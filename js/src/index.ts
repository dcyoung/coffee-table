import * as THREE from 'three';
import { CSG } from "three-csg-ts";
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { TransformControls } from 'three/examples/jsm/controls/TransformControls.js';
import { mergeBufferGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js';
import { EXRLoader } from 'three/examples/jsm/loaders/EXRLoader.js';
import { BathymetryContourGeometriesLoader } from './model-loader';

// Loading progress bar
const loadingManager = new THREE.LoadingManager();
loadingManager.onProgress = (url, loaded, total) => {
  const progressBar = document.getElementById("progress-bar") as HTMLProgressElement;
  progressBar.value = (loaded / total) * 100;
};
loadingManager.onLoad = () => {
  document.querySelector<HTMLElement>('.progress-bar-container').style.display = 'none';
}

const ASSETS_ROOT_PATH = "assets/";
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.x = -0.75;
camera.position.y = 0.5;
camera.position.z = 0.5;

// Renderer
const renderer = new THREE.WebGLRenderer();
renderer.physicallyCorrectLights = true;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
// renderer.exposure = 1.0;
renderer.toneMappingExposure = 1.25;
renderer.outputEncoding = THREE.sRGBEncoding;
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);
function onWindowResize() {
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}
window.addEventListener('resize', onWindowResize, false);

// Controls 
const controls = new OrbitControls(camera, renderer.domElement);
// const transformControls = new TransformControls(camera, renderer.domElement);
// const disableControl = (): void => {
//   transformControls.detach();
//   scene.remove(transformControls);
// }
// const controlRotation = (object: THREE.Mesh): void => {
//   transformControls.detach();
//   transformControls.attach(object);
//   transformControls.showY = true;
//   transformControls.showZ = false;
//   transformControls.showX = false;
//   transformControls.setMode('rotate');
//   transformControls.rotationSnap = Math.PI / 35;
//   scene.add(transformControls);
// }
// const controlPlacement = (object: THREE.Mesh): void => {
//   transformControls.detach();
//   transformControls.attach(object);
//   transformControls.showY = false;
//   transformControls.showZ = true;
//   transformControls.showX = true;
//   transformControls.setMode('translate');
//   scene.add(transformControls);
// }

// Materials
const tableTextureLoader = new THREE.TextureLoader(loadingManager).setPath(`${ASSETS_ROOT_PATH}textures/concrete_floor_worn_001/`);
const tableMaterial = new THREE.MeshStandardMaterial();
tableMaterial.envMapIntensity = 2.0;
const tableDiffMap = tableTextureLoader.load("diff_4k.jpg");
tableDiffMap.encoding = THREE.sRGBEncoding;
tableMaterial.map = tableDiffMap;
tableMaterial.metalnessMap = tableMaterial.roughnessMap = tableTextureLoader.load("arm_4k.jpg");
tableMaterial.normalMap = tableTextureLoader.load("nor_gl_4k.jpg");
// Glass material
const glassMaterial = new THREE.MeshPhysicalMaterial(
  {
    // thickness: 0.0,
    roughness: 0.8,
    clearcoat: 0.7,
    clearcoatRoughness: 0.0,
    transmission: 1.0,
    ior: 1.0,
    envMapIntensity: 17,
    color: '#5e82b7',
    attenuationColor: new THREE.Color(0xffe79e),
    attenuationDistance: 0.0,
  }
);

// Environment Map
const pmremGenerator = new THREE.PMREMGenerator(renderer);
pmremGenerator.compileEquirectangularShader();
new EXRLoader(loadingManager)
  .load(`${ASSETS_ROOT_PATH}env-maps/large_corridor_4k.exr`, function (texture) {
    let exrCubeRenderTarget = pmremGenerator.fromEquirectangular(texture);
    scene.environment = exrCubeRenderTarget.texture;
    scene.background = exrCubeRenderTarget.texture;
    tableMaterial.envMap = exrCubeRenderTarget.texture;
    tableMaterial.needsUpdate = true;
    glassMaterial.envMap = exrCubeRenderTarget.texture;
    glassMaterial.needsUpdate = true;
    texture.dispose();
  });


// Dimensions
const slabLongDim = 1.0;
const slabShortDim = 1.0;
const slabHeight = 0.118;
const maxWaterDepth = 0.8 * slabHeight;
const waterRotation = new THREE.Vector3(Math.PI / 2, 0, -Math.PI / 4);

// Slab body setup
const slabGeometry = new THREE.BoxGeometry(slabShortDim, slabHeight, slabLongDim);
const slabBodyPreCut = new THREE.Mesh(slabGeometry, tableMaterial);
slabBodyPreCut.position.y = 1.01 * (-slabHeight / 2);
slabBodyPreCut.updateMatrix();
let slabBody: THREE.Mesh = null;
let bathymetryMesh: THREE.Mesh = null;

// Layers setup
new BathymetryContourGeometriesLoader(loadingManager).load(
  `${ASSETS_ROOT_PATH}contour-layers/lake-tahoe`,
  maxWaterDepth,
  (contourGeometriesByLayer) => {
    // Create the merged bathymetry water mesh water 
    const bathymetryGeometry = mergeBufferGeometries(contourGeometriesByLayer.flat());
    bathymetryMesh = new THREE.Mesh(bathymetryGeometry, glassMaterial);
    bathymetryMesh.rotation.x = waterRotation.x;
    bathymetryMesh.rotation.z = waterRotation.z;
    scene.add(bathymetryMesh);
    // controlRotation(bathymetryMesh);
    // controlPlacement(bathymetryMesh);

    // Cutout the water from the tile to leave the bathymetry contour
    for (const contourGeometries of contourGeometriesByLayer) {
      const layerGeometry = mergeBufferGeometries(contourGeometries);
      const layerMesh = new THREE.Mesh(layerGeometry, glassMaterial);
      layerMesh.rotation.x = waterRotation.x;
      layerMesh.rotation.z = waterRotation.z;
      layerMesh.updateMatrix();
      if (slabBody == null) {
        slabBody = CSG.subtract(slabBodyPreCut, layerMesh);
      }
      else {
        slabBody = CSG.subtract(slabBody, layerMesh);
      }
    }
    scene.add(slabBody);
  },
  (err) => {
    throw err
  }
)

// Animate the mechanism
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const t_sec = clock.getElapsedTime();
  if (bathymetryMesh != null) {
    bathymetryMesh.position.y = 0.05 * (1 + Math.sin(0.5 * t_sec));
  }
  renderer.render(scene, camera);
};

animate();
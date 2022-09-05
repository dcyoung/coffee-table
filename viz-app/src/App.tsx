import './App.css';
import { Suspense } from "react";
import { Canvas } from "@react-three/fiber";
import { Environment, OrbitControls, Stats } from "@react-three/drei";
import CoasterMonterey from './components/coasters/monterey/coasterMonterey';
import LoadingScreen from './components/loadingScreen';

const App = (): JSX.Element => {
  return (
    <Suspense fallback={<LoadingScreen></LoadingScreen>}>
      <Canvas
        camera={{
          fov: 75,
          near: 0.1,
          far: 1000,
          position: [-75, 50, 50],
          up: [0, 1, 0],
        }}
      >
        <Environment
          background={true} // Whether to affect scene.background
          preset={'apartment'}
          path={'/'}
        />
        <CoasterMonterey></CoasterMonterey>
        <Stats />
        <OrbitControls />
      </Canvas>
    </Suspense>
  );
}

export default App;
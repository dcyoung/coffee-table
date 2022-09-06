import './App.css';
import { Canvas } from "@react-three/fiber";
import { Environment, OrbitControls, Stats } from "@react-three/drei";
import CoasterTarget from './components/coasterTarget';
import { Suspense } from 'react';
import { useControls } from 'leva';

const App = (): JSX.Element => {
  const { Selection } = useControls({
    Selection: {
      value: "monterey",
      options: ["monterey", "catalina"]
    },
  });
  
  return (
    <Canvas
      camera={{
        fov: 75,
        near: 0.1,
        far: 1000,
        position: [-75, 50, 50],
        up: [0, 1, 0],
      }}
    >
      <Suspense fallback={null}>
        <Environment
          background={true} // Whether to affect scene.background
          preset={'apartment'}
          path={'/'}
        />
        <CoasterTarget name={Selection}></CoasterTarget>
      </Suspense>
      <Stats />
      <OrbitControls />
    </Canvas>
  );
}

export default App;
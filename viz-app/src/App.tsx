import './App.css';
import { Canvas } from "@react-three/fiber";
import { ContactShadows, Environment, ScrollControls, Stats } from "@react-three/drei";
import { Suspense } from 'react';
import { useControls } from 'leva';
import CoasterTarget from './components/coasterTarget';

const App = (): JSX.Element => {
  const { Selection } = useControls({
    Selection: {
      value: "monterey",
      options: ["monterey", "catalina", "san-francisco bay", "lake tahoe"]
    },
  });

  return (
    <Suspense fallback={null}>
      <Canvas
        shadows
        camera={{
          fov: 75,
          near: 0.1,
          far: 1000,
          position: [-75, 50, 50],
          up: [0, 1, 0],
        }}
      >
        <ScrollControls
          pages={5} // Each page takes 100% of the height of the canvas
          distance={1} // A factor that increases scroll bar travel (default: 1)
          damping={4} // Friction, higher is faster (default: 4)
          horizontal={false}
          infinite={false}
        >
          <Environment
            background={false}
            preset={'apartment'}
          />
          <CoasterTarget name={Selection}></CoasterTarget>
          <ContactShadows
            position={[0, -75, 0]}
            opacity={0.25}
            scale={500}
            blur={1.5}
            far={800} />
          <Stats />
        </ScrollControls>
      </Canvas>
    </Suspense>
  );
}

export default App;
import { Html, useProgress } from "@react-three/drei";

export const LoadingScreen = (): JSX.Element => {
  const { active, progress, errors, item, loaded, total } = useProgress()
  return (<Html center>{progress} % total</Html>);
  // return (<span>loading...</span>);
}

export default LoadingScreen;
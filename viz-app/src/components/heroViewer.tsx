import { useControls } from "leva";
import CoasterCanvas from "./coasterCanvas";

const HeroViewer = (): JSX.Element => {
  const { Selection, ManualControl } = useControls({
    Selection: {
      value: "monterey",
      options: ["monterey", "catalina", "san-francisco bay", "lake tahoe"],
    },
    ManualControl: true,
  });

  return <CoasterCanvas name={Selection} scrollable={!ManualControl} />;
};

export default HeroViewer;

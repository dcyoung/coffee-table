import ModelBase from "./modelBase";

export interface CoasterBaseProps {
  urlCoaster: string;
  urlWater: string;
}

export const CoasterBase = ({
  urlCoaster,
  urlWater,
  ...props
}: CoasterBaseProps): JSX.Element => {
  return (
    <group {...props}>
      <ModelBase url={urlCoaster}></ModelBase>
      <ModelBase url={urlWater}></ModelBase>
    </group>
  );
}

export default CoasterBase;
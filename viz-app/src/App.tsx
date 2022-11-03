// import SalesPage from "./components/sales/salesPage";
// const App = (): JSX.Element => {
//   return <SalesPage />;
// };

import HeroViewer from "./components/heroViewer";
const App = (): JSX.Element => {
  return (
    <div className="fixed m-0 h-full w-screen overflow-hidden bg-white p-0 font-sans text-black">
      <HeroViewer />
    </div>
  );
};

export default App;

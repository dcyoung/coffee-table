const SalesPage = (): JSX.Element => {
  return (
    <div className="snap h-screen max-h-screen snap-y snap-mandatory overflow-y-scroll text-center text-black">
      {/* <div className="relative h-5/6 bg-red-400">
        <div className="absolute top-1/4 left-1/4 h-1/2 w-1/2 bg-yellow-400"></div>
      </div> */}
      <div className="h-5/6 snap-center bg-red-400">
        <h1>Page1</h1>
      </div>
      <div className="h-5/6 snap-center bg-blue-400">
        <h1>Page2</h1>
      </div>
      <div className="h-5/6 snap-center bg-green-400">
        <h1>Page3</h1>
      </div>
    </div>
  );
};
export default SalesPage;

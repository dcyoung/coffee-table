const SalesPage = (): JSX.Element => {
  return (
    <main className="snap mx-auto h-screen max-h-screen snap-y snap-mandatory overflow-y-scroll bg-white text-black">
      {/* <div className="relative h-5/6 bg-red-400">
        <div className="absolute top-1/4 left-1/4 h-1/2 w-1/2 bg-yellow-400"></div>
      </div> */}
      <div className="relative h-5/6 snap-center sm:text-center lg:text-left">
        <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl md:text-6xl">
          Some Snazzy Title
        </h1>
        <p className="text-base text-gray-500 sm:mx-auto sm:max-w-xl sm:text-lg md:mt-5 md:text-xl lg:mx-0">
          Anim aute id magna aliqua ad ad non deserunt sunt. Qui irure qui lorem
          cupidatat commodo. Elit sunt amet fugiat veniam occaecat fugiat
          aliqua.
        </p>
        <div className="mt-5 sm:mt-8 sm:flex sm:justify-center lg:justify-start">
          <div className="rounded-md shadow">
            <a
              href="#"
              className="flex w-full items-center justify-center rounded-md border border-transparent bg-indigo-600 px-8 py-3 text-base font-medium text-white hover:bg-indigo-700 md:py-4 md:px-10 md:text-lg"
            >
              Get started
            </a>
          </div>
          <div className="mt-3 sm:mt-0 sm:ml-3">
            <a
              href="#"
              className="flex w-full items-center justify-center rounded-md border border-transparent bg-indigo-100 px-8 py-3 text-base font-medium text-indigo-700 hover:bg-indigo-200 md:py-4 md:px-10 md:text-lg"
            >
              Live demo
            </a>
          </div>
        </div>
        <div className="absolute lg:inset-y-0 lg:right-0 lg:w-1/2">
          <img
            className="h-56 w-full object-cover sm:h-72 md:h-96 lg:h-full lg:w-full"
            src="https://images.unsplash.com/photo-1551434678-e076c223a692?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=2850&q=80"
            alt=""
          />
        </div>
      </div>
      <div className="h-1/6 bg-blue-400">Spacer</div>
      <div className="h-5/6 snap-center">
        <h1>Page #2</h1>
      </div>
      <div className="h-1/6  bg-green-400">Spacer</div>
      <div className="h-5/6 snap-center">
        <h1>Page #3</h1>
      </div>
      <div className="h-1/6 bg-red-400">Spacer</div>
    </main>
  );
};
export default SalesPage;

import asyncio
from typing import Optional
from dotenv import load_dotenv

from ..utils import get_env, read_files
from .utils import create_form_data, send_request


class AWClient:
    """
    Anything World API Client

                        .-. .-.    _                                   .-.     .-.
                       .' `.: :   :_;                                  : :     : :
     .--.  ,-.,-..-..-.`. .': `-. .-.,-.,-. .--.   .-..-..-. .--. .--. : :   .-' :
    ' .; ; : ,. :: :; : : : : .. :: :: ,. :' .; :  : `; `; :' .; :: ..': :_ ' .; :
    `.__,_;:_;:_;`._. ; :_; :_;:_;:_;:_;:_;`._. ;  `.__.__.'`.__.':_;  `.__;`.__.'
                  .-. :                     .-. :
                  `._.'                     `._.'

   Provides an interface to the Anything World API. It allows to send requests to the
   API to animate 3D models and retrieve them once they are done.
   """

    # Stage names that identify the end of a process for a given endpoint name
    _finished_stages = {
        "animate": {
            # In these stages, basic formats are already generated
            "default": [
                "format_conversion",
                "thumbnails_generation",
                "migrate_animation_finished"
            ],
            # In these stages, extra formats are already generated
            "extra_formats": [
                "formats_conversion_finished"
            ]
        }
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize an instance of AWClient.

        :param api_key: str, API key to use for requests. If not provided, it will
            be read from the environment variable AW_API_KEY.
        """
        load_dotenv()
        self.api_key = api_key if api_key else get_env('AW_API_KEY')
        self.api_url = get_env('AW_API_URL')
        self.polling_url = get_env('AW_POLLING_URL')
        try:
            mode = get_env('AW_MODE')
            self.is_staging = mode == 'staging'
        except Exception:
            self.is_staging = False


    async def find_by_name(self, model_name: str) -> dict:
        """
        Asynchronously queries the Anything World API for a given model name.

        :param model_name: str, the name of the model to query.
        :return: dict, the JSON response from the API decoded as a dict.
        """
        return await self._anything(model_name=model_name)


    async def find(self, search_query: str) -> dict:
        """
        Asynchronously queries the Anything World API for a given search query.

        :param search_query: str, the search query to query.
        :return: dict, the JSON response from the API decoded as a dict.
        """
        return await self._anything(search_query=search_query)


    async def animate(
            self,
            files_dir: str,
            model_name: str,
            model_type: str,
            is_symmetric: bool = True) -> dict:
        """
        Asynchronously sends a request to animate a model.

        This function reads files from the specified directory, creates form data from the files and additional data,
        and sends a POST request to the API to animate the model.

        :param files_dir: str, the directory where the files to be animated are located.
        :param model_name: str, the name of the model to be animated.
        :param model_type: str, the type of the model to be animated.
        :param is_symmetric: bool, optional, a flag indicating whether the model is symmetric. Defaults to True.

        :return: dict, the JSON response from the API decoded as a dict.
        """
        data = {
            "api_key": self.api_key,
            "model_name": model_name,
            "model_type": model_type,
            "symmetry": "true" if is_symmetric else "false"
        }
        form_data = create_form_data(read_files(files_dir), data)
        params = {"staging": "true"} if self.is_staging else {}
        return await send_request(
            url=f"{self.api_url}/animate",
            method="POST",
            data=form_data,
            params=params
        )


    async def get_animated_model(
            self,
            model_id: str,
            extra_formats: bool = False,
            waiting_time: Optional[int] = 5,
            warmup_time: Optional[int] = 0,
            verbose: Optional[bool] = False) -> dict:
        """
        Asynchronously retrieves an animated model by polling.

        This function sends a GET request to the API to retrieve the animated model. It polls the API until the model
        reaches the finished stage expected for the /animate endpoint, waiting a specified amount of time
        between each request.

        The request will look if the model is done animated and with the
        basic formats only generated (`.glb`, `.fbx`). If you want to wait until all
        formats are generated as well (`.gltf`, `.dae`), set the
        `extra_formats` param to `True`.   

        :param model_id: str, the ID of the model to retrieve.
        :param extra_formats: bool, optional, a flag indicating if the model
            should have extra formats in the response or not. Defaults to False.
        :param waiting_time: int, optional, the amount of time to wait between each request in seconds. Defaults to 5.
        :param warmup_time: int, optional, the amount of time to wait before sending the first request in seconds.
            This is useful specially for users with low connectivity, to avoid unnecessary requests, given that for
            some models the API takes a while to the model ready. Defaults to 0.  
        :param verbose: bool, optional, a flag indicating whether to print detailed information about each request.
            Defaults to False.
        :return: dict, the JSON response from the API decoded as a dict.
        """
        expected_formats = "extra_formats" if extra_formats else "default"
        return await self._get_model_by_polling(
            model_id,
            expected_stages=self._finished_stages["animate"][expected_formats],
            waiting_time=waiting_time,
            warmup_time=warmup_time,
            verbose=verbose)


    async def is_animation_done(self, model_id: str, extra_formats: bool=False) -> bool:
        """
        Checks if the animation of a model is done.

        This function sends a request to the API to check if the animation of the specified model is done.

        The request will look if the model is done animated and with the
        basic formats only generated (`.glb`, `.fbx`). If you want to wait until all
        formats are generated as well (`.gltf`, `.dae`), set the
        `extra_formats` param to `True`.   

        :param model_id: str, the ID of the model to check.
        :param extra_formats: bool, optional, a flag indicating if the model
            should have extra formats in the response or not. Defaults to False.
        :return: bool, True if the animation is done, False otherwise.
        """
        return await self._is_model_done(model_id, "animate", extra_formats)


    async def get_model(self, model_id: str) -> dict:
        """
        Retrieves a model.

        This function sends a GET request to the API to retrieve the specified model. If the response is a list with
        one item, it returns the item. Otherwise, it returns the whole response.

        :param model_id: str, the ID of the model to retrieve.
        :return: dict, the JSON response from the API decoded as a dict.
        """
        params = {
            'key': self.api_key,
            'id': model_id,
            'stage': 'done',
        }
        if self.is_staging:
            params["staging"] = "true"
        res = await send_request(
            url=self.polling_url,
            method="GET",
            params=params)
        if isinstance(res, list) and len(res) == 1:
            return res[0]
        return res


    async def _anything(
            self,
            model_name: Optional[str] = None,
            search_query: Optional[str] = None,
            fuzzy: Optional[bool] = True,
            ) -> dict:
        """
        Asynchronously queries the Anything World API for a given model name or search query.

        :param model_name: str, optional, the name of the model to query.
        :param search_query: str, optional, the search query to query.
        :param fuzzy: bool, optional (default: true), whether to perform fuzzy/approximate matching of
            the query with the database entries' fields, using a custom implementation
            of the edit distance algorithm.
        :return: dict, the JSON response from the API decoded as a dict.
        """
        # Required params
        data = {
            "key": self.api_key
        }
        if self.is_staging:
            data["staging"] = "true"
        # Optional params
        if model_name:
            data["name"] = model_name
        if search_query:
            data["search"] = search_query
        if fuzzy:
            data["fuzzy"] = str(fuzzy).lower()

        return await send_request(
            url=f"{self.api_url}/anything",
            method="GET",
            params=data
        )


    async def _get_model_by_polling(
            self,
            model_id: str,
            expected_stages: list,
            waiting_time: Optional[int] = 5,
            warmup_time: Optional[int] = 0,
            verbose: Optional[bool] = False) -> dict:
        """
        Retrieves a model by polling until it reaches the expected stage.

        This function sends a GET request to the API to retrieve the specified model. It polls the API until the model
        reaches the expected stage, waiting a specified amount of time between each request.

        :param model_id: str, the ID of the model to retrieve.
        :param expected_stages: str, the possible stages that the model is expected to reach to
            be considered done.
        :param waiting_time: int, optional, the amount of time to wait between each request in seconds. Defaults to 5.
        :param warmup_time: int, optional, the amount of time to wait before sending the first request in seconds.
            This is useful specially for users with low connectivity, to avoid unnecessary requests, given that for
            some models the API takes a while to the model ready. Defaults to 0.  
        :param verbose: bool, optional, a flag indicating whether to print detailed information about each request.
            Defaults to False.
        :return: dict, the JSON response from the API decoded as a dict.
        """
        if warmup_time > 0:
            await asyncio.sleep(warmup_time)
        attempt_count = 0

        while True:
            attempt_count += 1
            status_prefix = f"Polling attempt #{attempt_count}."
            try:
                model_json = await self.get_model(model_id)
            except Exception as e:
                if verbose:
                    print(f"{status_prefix} Error: {e}")
                return
            if "stage" in model_json:
                model_stage = model_json["stage"]
                if model_stage in expected_stages:
                    if verbose:
                        print(f"{status_prefix} Done.")
                    return model_json
            else:
                if verbose:
                    print(f"{status_prefix} Model {model_id} is not ready yet...")
            await asyncio.sleep(waiting_time)


    async def _is_model_done(
            self,
            model_id: str,
            endpoint: str,
            extra_formats: bool=False) -> bool:
        """
        Check if a model is done for a given endpoint.

        :param model_id: str, the ID of the model to check.
        :param endpoint: str, the endpoint to check.
        :param extra_formats: bool, optional, a flag indicating if the model
            should have extra formats in the response or not. Defaults to False.
        :return: bool, True if the model is done, False otherwise.
        """
        required_formats = "extra_formats" if extra_formats else "default"
        expected_stages = self._finished_stages[endpoint][required_formats]
        res = await self.get_model(model_id)
        if "stage" in res:
            return res["stage"] in expected_stages
        return False


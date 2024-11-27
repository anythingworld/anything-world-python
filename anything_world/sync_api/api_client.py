import time

from typing import Optional
from dotenv import load_dotenv

from ..settings import AW_API_URL, AW_POLLING_URL, AW_GENERATED_POLLING_URL
from ..utils import get_env, read_file, read_files, create_temporary_folder
from .utils import create_form_data, send_request, download_file

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
   API to generate, animate 3D models and retrieve them once they are done.
   """

    # Stage names that identify the end of a process for a given endpoint name
    _finished_stages = {
        "animate": {
            # In these stages, basic formats are already generated
            "default": [
                "thumbnails_generation_finished",
                "formats_conversion_finished",
                "migrate_animation_finished"
            ],
            # In these stages, extra formats are already generated
            "extra_formats": [
                "formats_conversion_finished"
            ]
        },
        "generate": {
            "default": [
                "thumbnails_generation_finished",
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
        self.api_url = AW_API_URL
        self.polling_url = AW_POLLING_URL
        self.generated_polling_url = AW_GENERATED_POLLING_URL
        try:
            mode = get_env('AW_MODE')
            self.is_staging = mode == 'staging'
        except Exception:
            self.is_staging = False


    def find_by_name(self, model_name: str) -> dict:
        """
        Queries the Anything World API for a given model name.

        :param model_name: str, the name of the model to query.
        :return: dict, the JSON response from the API decoded as a dict.
        """
        return self._anything(model_name=model_name)


    def find(self, search_query: str) -> dict:
        """
        Queries the Anything World API for a given search query.

        :param search_query: str, the search query to query.
        :return: dict, the JSON response from the API decoded as a dict.
        """
        return self._anything(search_query=search_query)


    def animate(
            self,
            files_dir: str,
            model_name: str,
            model_type: str = None,
            auto_rotate: bool = True,
            is_symmetric: bool = True) -> dict:
        """
        Sends a request to animate a model.

        This function reads files from the specified directory, creates form data from the files and additional data,
        and sends a POST request to the API to animate the model.

        :param files_dir: str, the directory where the files to be animated are located.
        :param model_name: str, the name of the model to be animated.
        :param model_type: str, optional, the type of the model to be animated. If not given, it will set the
            `auto_classify` request parameter as "true", allowing the AI to find the model type automatically.
        :param auto_rotate: bool, optional, if the AI should automatically fix rotation of the model or not.
            Defaults to True.
        :param is_symmetric: bool, optional, a flag indicating whether the model is symmetric. Defaults to True.

        :return: dict, the JSON response from the API decoded as a dict.
        """
        data = {
            "key": self.api_key,
            "model_name": model_name,
            "model_type": model_type if model_type else "",
            "symmetry": "true" if is_symmetric else "false",
            "auto_rotate": "true" if auto_rotate else "false",
            "auto_classify": "true" if not model_type else "false",
            "platform": "python"
        }
        form_data = create_form_data(read_files(files_dir), {})
        params = {"staging": "true"} if self.is_staging else {}
        return send_request(
            url=f"{self.api_url}/animate",
            method="POST",
            data=data,
            files=form_data,
            params=params
        )[0]


    def get_animated_model(
            self,
            model_id: str,
            extra_formats: bool = False,
            waiting_time: Optional[int] = 5,
            warmup_time: Optional[int] = 0,
            verbose: Optional[bool] = False) -> dict:
        """
        Retrieves an animated model by polling.

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
        return self._get_model_by_polling(
            model_id,
            url=self.polling_url,
            expected_stages=self._finished_stages["animate"][expected_formats],
            waiting_time=waiting_time,
            warmup_time=warmup_time,
            verbose=verbose)


    def is_animation_done(self, model_id: str, extra_formats: bool=False) -> bool:
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
        return self._is_model_done(model_id, "animate", extra_formats)


    def get_model(self, model_id: str) -> dict:
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
        res = send_request(
            url=self.polling_url,
            method="GET",
            params=params)
        if isinstance(res, list) and len(res) == 1:
            return res[0]
        return res


    def generate_from_text(
            self,
            prompt: str,
            refine_prompt: Optional[bool] = True,
            can_be_public: Optional[bool] = False,
            can_use_for_internal_improvements: Optional[bool] = False
        ) -> dict:
        """
        Sends a request to generate a 3D model from a text prompt.

        This function sends a POST request to the API to generate a 3D model from a text prompt.

        :param prompt: str, the text prompt to generate the 3D model from.
        :param refine_prompt: bool, optional, whether to refine the prompt or not. Defaults to True.
        :param can_be_public: bool, optional, whether the generated model can be public or not. Defaults to False.
        :param can_use_for_internal_improvements: bool, optional, whether the generated model can be used for internal
            improvements or not. Defaults to False.
        :return: dict, the JSON response from the API decoded as a dict.
        """
        data = {
            "key": self.api_key,
            "text_prompt": prompt,
            "refine_prompt": "true" if refine_prompt else "false",
            "can_use_for_internal_improvements": "true" if can_use_for_internal_improvements else "false",
            "can_be_public": "true" if can_be_public else "false",
            "platform": "python"
        }
        params = {"staging": "true"} if self.is_staging else {}
        return send_request(
            url=f"{self.api_url}/text-to-3d",
            method="POST",
            data=data,
            params=params
        )[0]


    def generate_from_image(
            self,
            file_path: str,
            model_name: str,
            can_be_public: Optional[bool] = False,
            can_use_for_internal_improvements: Optional[bool] = False,
        ) -> dict:
        """
        Sends a request to generate a 3D model from an image.

        :param file_path: str, the path to the image file to generate the 3D model from.
        :param model_name: str, the name of the model to be animated.
        :param model_type: str, optional, the type of the model to be animated. If not given, it will set the
            `auto_classify` request parameter as "true", allowing the AI to find the model type automatically.
        :param auto_rotate: bool, optional, if the AI should automatically fix rotation of the model or not.
            Defaults to True.
        :param is_symmetric: bool, optional, a flag indicating whether the model is symmetric. Defaults to True.

        :return: dict, the JSON response from the API decoded as a dict.
        """
        data = {
            "key": self.api_key,
            "model_name": model_name,
            "can_be_public": "true" if can_be_public else "false",
            "can_use_for_internal_improvements": "true" if can_use_for_internal_improvements else "false",
            "platform": "python"
        }
        params = {"staging": "true"} if self.is_staging else {}

        file_tuple = read_file(file_path)
        file = open(file_tuple[1], "rb")

        return send_request(
            url=f"{self.api_url}/image-to-3d",
            method="POST",
            data=data,
            params=params,
            files=[('files', file)]
        )[0]


    def generate_animated_from_text(
            self,
            prompt: str,
            refine_prompt: Optional[bool] = True,
            can_be_public: Optional[bool] = False,
            can_use_for_internal_improvements: Optional[bool] = False
        ) -> dict:
        """
        Sends a request to generate an animated 3D model from a text prompt.

        This function sends a POST request to the API to generate an animated 3D model from a text prompt.

        :param prompt: str, the text prompt to generate the 3D model from.
        :param refine_prompt: bool, optional, whether to refine the prompt or not. Defaults to True.
        :param can_be_public: bool, optional, whether the generated model can be public or not. Defaults to False.
        :param can_use_for_internal_improvements: bool, optional, whether the generated model can be used for internal
            improvements or not. Defaults to False.
        :return: dict, the JSON response from the API decoded as a dict.
        """
        res = self.generate_from_text(prompt, refine_prompt, can_be_public, can_use_for_internal_improvements)
        res = self.get_generated_model(res["model_id"])

        # Download mesh file to a temporary folder
        tmp_folder = create_temporary_folder()
        download_file(res["model"]["mesh"]["glb"], f"{tmp_folder}/model.glb")

        res = self.animate(tmp_folder, res['name'], auto_rotate=True, is_symmetric=True)
        res = self.get_animated_model(res['model_id'])

        return res


    def generate_animated_from_image(
            self,
            file_path: str,
            model_name: str,
            can_be_public: Optional[bool] = False,
            can_use_for_internal_improvements: Optional[bool] = False
        ) -> dict:
        """
        Sends a request to generate an animated 3D model from a given image.

        This function sends a POST request to the API to generate an animated 3D model from a given image.

        :param file_path: str, the path to the image file to generate the 3D model from.
        :param model_name: str, the name of the model to be animated.
        :param can_be_public: bool, optional, whether the generated model can be public or not. Defaults to False.
        :param can_use_for_internal_improvements: bool, optional, whether the generated model can be used for internal
            improvements or not. Defaults to False.
        :return: dict, the JSON response from the API decoded as a dict.
        """
        res = self.generate_from_image(file_path, model_name, can_be_public, can_use_for_internal_improvements)
        res = self.get_generated_model(res["model_id"])

        # Download mesh file to a temporary folder
        tmp_folder = create_temporary_folder()
        download_file(res["model"]["mesh"]["glb"], f"{tmp_folder}/model.glb")

        res = self.animate(tmp_folder, res['name'], auto_rotate=True, is_symmetric=True)
        res = self.get_animated_model(res['model_id'])

        return res


    def get_generated_model(
            self,
            model_id: str,
            waiting_time: Optional[int] = 5,
            warmup_time: Optional[int] = 0,
            verbose: Optional[bool] = False) -> dict:
        """
        Retrieves a generated model by polling.

        This function sends a GET request to the API to retrieve the generated model. It polls the API until the model
        reaches the finished stage expected for endpoint, waiting a specified amount of time
        between each request.

        :param model_id: str, the ID of the model to retrieve.
        :param waiting_time: int, optional, the amount of time to wait between each request in seconds. Defaults to 5.
        :param warmup_time: int, optional, the amount of time to wait before sending the first request in seconds.
            This is useful specially for users with low connectivity, to avoid unnecessary requests, given that for
            some models the API takes a while to the model ready. Defaults to 0.  
        :param verbose: bool, optional, a flag indicating whether to print detailed information about each request.
            Defaults to False.
        :return: dict, the JSON response from the API decoded as a dict.
        """    
        return self._get_model_by_polling(
            model_id,
            expected_stages=self._finished_stages["generate"]["default"],
            url=self.generated_polling_url,
            waiting_time=waiting_time,
            warmup_time=warmup_time,
            verbose=verbose)


    def _anything(
            self,
            model_name: Optional[str] = None,
            search_query: Optional[str] = None,
            fuzzy: Optional[bool] = True,
            ) -> dict:
        """
        Queries the Anything World API for a given model name or search query.

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

        return send_request(
            url=f"{self.api_url}/anything",
            method="GET",
            params=data
        )


    def _get_model(self, model_id: str, url: str) -> dict:
        """
        Retrieves a model.

        This function sends a GET request to the API to retrieve the specified model. If the response is a list with
        one item, it returns the item. Otherwise, it returns the whole response.

        :param model_id: str, the ID of the model to retrieve.
        :param url: str, the URL to send the request to.
        :return: dict, the JSON response from the API decoded as a dict.
        """
        params = {
            'key': self.api_key,
            'id': model_id,
            'stage': 'done',
        }
        if self.is_staging:
            params["staging"] = "true"
        res, status = send_request(
            url=url,
            method="GET",
            params=params)
        if isinstance(res, list) and len(res) == 1:
            return res[0], status
        return res, status


    def _get_model_by_polling(
            self,
            model_id: str,
            expected_stages: list,
            url: str,
            waiting_time: Optional[int] = 5,
            warmup_time: Optional[int] = 0,
            verbose: Optional[bool] = False) -> dict:
        """
        Retrieves a model by polling until it reaches the expected stage.

        This function sends a GET request to the API to retrieve the specified model. It polls the API until the model
        reaches the expected stage, waiting a specified amount of time between each request.

        :param model_id: str, the ID of the model to retrieve.
        :param expected_stages: list, the possible stages that the model is expected to reach to
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
            time.sleep(warmup_time)
        attempt_count = 0

        while True:
            attempt_count += 1
            status_prefix = f"Polling attempt #{attempt_count}."
            try:
                model_json, status = self._get_model(model_id, url)
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
            elif status == 200:
                return model_json
            else:
                if verbose:
                    print(f"{status_prefix} Model {model_id} is not ready yet...")
            time.sleep(waiting_time)


    def _is_model_done(
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
        res = self.get_model(model_id)
        if "stage" in res:
            return res["stage"] in expected_stages
        return False


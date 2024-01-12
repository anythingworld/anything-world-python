import asyncio
from typing import Optional
from dotenv import load_dotenv

from .utils import get_env, read_files, create_form_data, send_request


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
        "animate": "thumbnails_generation_finished"
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


    async def anything(
            self,
            model_name: Optional[str] = None,
            search_query: Optional[str] = None,
            guid: Optional[int] = None,
            fuzzy: Optional[bool] = None,
            include_poly: Optional[bool] = None,
            include_tags: Optional[bool] = None,
            include_taxonomy: Optional[bool] = None,
            include_categories: Optional[bool] = None,
            vehicle_only: Optional[bool] = None,
            segmented_only: Optional[bool] = None,
            rigged_only: Optional[bool] = None,
            animated_only: Optional[bool] = None,
            sort: Optional[str] = None,
            descending: Optional[bool] = None,
            obj_wrap: Optional[bool] = None,
            increase_popularity: Optional[bool] = None
            ) -> dict:
        """
        Asynchronously queries the Anything World API for a given model name or search query.

        :param model_name: str, optional, the name of the model to query.
        :param search_query: str, optional, the search query to query.
        :param guid: four digit int, optional, GUID of the model if the name/search
            parameter uses the base name without hashtag and GUID.
        :param fuzzy: bool, optional (default: true), whether to perform fuzzy/approximate matching of
            the query with the database entries' fields, using a custom implementation
            of the edit distance algorithm.
        :param includePoly: bool, optional (default: true), whether to search for matches in PolyModels
            instead of just in anythings collection.
        :param includeTags: bool, optional (default: true), whether to accept search results based on
            query-tag matches.
        :param includeTaxonomy: bool, optional (default: true), whether to accept search results based
            on query-taxonomy matches.
        :param includeCategories: bool, optional (default: true), whether to include a themeCategories
            field in each returned entry. Those categories are calculated based on the tags, taxonomy
            and entity field of entries. The possible categories are: “animal“, “architecture“,
            “art”, “vehicle”, “character”, “culture”, “electronic”, “fashion”, “food”, “furniture”,
            “music”, “nature”, “news”, “people”, “place”, “science”, “sports”, “weapon”,
            plus a fall-back category “other“ used when none of the others is found suitable. 
        :param vehicleOnly: bool, (default: false), whether to return only entries whose type is
            vehicle-based. Only use it in search mode.
        :param segmentedOnly: bool, (default: false), whether to return only entries that have segmented
            parts (ignoring those that have a single part since they have no split). Only use it in search mode.
        :param riggedOnly: bool, (default: false), whether to return only entries that have a valid rig.
            Only use it in search mode.
        :param animatedOnly: bool, (default: false), whether to return only entries that have a valid
            rig with animations. Only use it in search mode.
        :param sort: str in [“default“, “popularity“, “vote“, “lexicographical“], (default: “default“), how to
            arrange search results. The default option applies query matching relevance, in the sense
            that exact matches come first, then fuzzy matches with increasing edit distance. In the case of tie,
            anythings results come before PolyModels results, and in case of tie there too, lexicographical
            order is used. The popularity option gives results in order of popularity field, the vote one in
            order of voteScore field, and the lexicographical option is self-explanatory.
        :param descending: bool, (default: true), whether to provide a descending sort given the selected
            sort criteria, ascending otherwise.
        :param objWrap: bool, (default: false), wrap response in a top-level “models“ object instead of having
            array as top-level element.
        :param increasePopularity: bool, (default: false), whether to increase the popularity of the returned item,
            only valid for the name mode.
        :return: dict, the JSON response from the API decoded as a dict.
        """
        # Required params
        data = {
            "key": self.api_key,
        }
        # Optional params
        if model_name:
            data["name"] = model_name
        if search_query:
            data["search"] = search_query
        if guid:
            data["guid"] = guid
        if fuzzy:
            data["fuzzy"] = fuzzy
        if include_poly:
            data["includePoly"] = include_poly
        if include_tags:
            data["includeTags"] = include_tags
        if include_taxonomy:
            data["includeTaxonomy"] = include_taxonomy
        if include_categories:
            data["includeCategories"] = include_categories
        if vehicle_only:
            data["vehicleOnly"] = vehicle_only
        if segmented_only:
            data["segmentedOnly"] = segmented_only
        if rigged_only:
            data["riggedOnly"] = rigged_only
        if animated_only:
            data["animatedOnly"] = animated_only
        if sort:
            data["sort"] = sort
        if descending:
            data["descending"] = descending
        if obj_wrap:
            data["objWrap"] = obj_wrap
        if increase_popularity:
            data["increasePopularity"] = increase_popularity

        return await send_request(
            url=f"{self.api_url}/anything",
            method="GET",
            params=data
        )


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
        return await send_request(
            url=f"{self.api_url}/run_all",
            method="POST",
            data=form_data
        )


    async def get_animated_model(
            self,
            model_id: str,
            waiting_time: Optional[int] = 5,
            verbose: Optional[bool] = False) -> dict:
        """
        Asynchronously retrieves an animated model by polling.

        This function sends a GET request to the API to retrieve the animated model. It polls the API until the model
        reaches the finished stage expected for the /animate endpoint, waiting a specified amount of time
        between each request.

        :param model_id: str, the ID of the model to retrieve.
        :param waiting_time: int, optional, the amount of time to wait between each request in seconds. Defaults to 5.
        :param verbose: bool, optional, a flag indicating whether to print detailed information about each request.
            Defaults to False.
        :return: dict, the JSON response from the API decoded as a dict.
        """    
        return await self.get_model_by_polling(
            model_id,
            expected_stage=self._finished_stages["animate"],
            waiting_time=waiting_time,
            verbose=verbose)


    async def is_animation_done(self, model_id: str) -> bool:
        """
        Checks if the animation of a model is done.

        This function sends a request to the API to check if the animation of the specified model is done.

        :param model_id: str, the ID of the model to check.
        :return: bool, True if the animation is done, False otherwise.
        """
        return await self._is_model_done(model_id, "animate")


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
            'staging': 'true'
        }
        res = await send_request(
            url=self.polling_url,
            method="GET",
            params=params)
        if isinstance(res, list) and len(res) == 1:
            return res[0]
        return res


    async def get_model_by_polling(
            self,
            model_id: str,
            expected_stage: str,
            waiting_time: Optional[int] = 5,
            warmup_time: Optional[int] = 0,
            verbose: Optional[bool] = False) -> dict:
        """
        Retrieves a model by polling until it reaches the expected stage.

        This function sends a GET request to the API to retrieve the specified model. It polls the API until the model
        reaches the expected stage, waiting a specified amount of time between each request.

        :param model_id: str, the ID of the model to retrieve.
        :param expected_stage: str, the stage that the model is expected to reach.
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
                if model_stage == expected_stage:
                    if verbose:
                        print(f"{status_prefix} Done.")
                    return model_json
            else:
                if verbose:
                    print(f"{status_prefix} Model is not ready yet...")
            await asyncio.sleep(waiting_time)


    async def _is_model_done(self, model_id: str, endpoint: str) -> bool:
        res = await self.get_model(model_id)
        if "stage" in res:
            return res["stage"] == self._finished_stages[endpoint]
        return False


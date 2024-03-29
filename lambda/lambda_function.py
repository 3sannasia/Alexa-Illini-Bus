# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response
import inflect
import requests

import os
import boto3

import os
import boto3

from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_dynamodb.adapter import DynamoDbAdapter

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ddb_region = os.environ.get("DYNAMODB_PERSISTENCE_REGION")
ddb_table_name = os.environ.get("DYNAMODB_PERSISTENCE_TABLE_NAME")

ddb_resource = boto3.resource("dynamodb", region_name=ddb_region)
dynamodb_adapter = DynamoDbAdapter(
    table_name=ddb_table_name, create_table=False, dynamodb_resource=ddb_resource
)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Check if the user has a favorite stop already

        speak_output = "Tell me your bus stop by saying use then your bus stop name."

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


def is_ordinal_string(s: str):
    if s.endswith("rd") or s.endswith("th") or s.endswith("st") or s.endswith("nd"):
        # Remove the suffix and check if the remaining part is a number
        number_part = s[:-2]
        if number_part.isdigit():
            return True
    return False


def convert_ordinal(intent_request: str):
    split_response = intent_request.split(" ")
    for i in range(len(split_response)):
        if is_ordinal_string(split_response[i]):
            p = inflect.engine()
            split_response[i] = p.number_to_words(split_response[i])
    intent_request = " ".join(split_response)

    return intent_request


class BusStopSetterHandler(AbstractRequestHandler):
    """Handler for Bus Stop Setter Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("BusStopSetter")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_request = str(
            handler_input.request_envelope.request.intent.slots["stop"].value
        )
        speak_output = ""
        intent_request = convert_ordinal(intent_request)
        mtd_autocomplete_api_url = (
            f"https://search.mtd.org/v1.0.0/stop/suggest/{intent_request}"
        )
        autocomplete_response = requests.get(mtd_autocomplete_api_url)
        if (
            autocomplete_response.status_code != 200
            or autocomplete_response.json() == []
        ):
            speak_output = "Bus stop not found"

        autocomplete_bus_id = str(autocomplete_response.json()[0]["result"]["id"])

        def format_for_alexa(bus_data):
            formatted_output = ""
            for bus, time in bus_data:
                formatted_output += f"{bus}: {time} minutes \n"
            return formatted_output.rstrip()

        # Added the get departures
        param = {
            "stop_id": autocomplete_bus_id,
            "pt": 60,
        }
        response = requests.get(
            "https://developer.mtd.org/api/v2.2/JSON/getdeparturesbystop?key={}".format(
                os.getenv("MTD_API_KEY")
            ),
            params=param,
        )

        bus_list = []

        if response.status_code == 200:
            response_json = response.json()
            bus_arrival_time_list = []
            for departure in response_json["departures"]:
                bus_arrival_time_list.append(
                    [departure["headsign"], departure["expected_mins"]]
                )
            bus_list = bus_arrival_time_list
            speak_output = format_for_alexa(bus_list)
        else:
            speak_output = "No buses reported"

        # Cannot use autocomplete name because that includes & value and breaks alexa

        return (
            handler_input.response_builder.speak(speak_output)
            # .ask(speak_output)
            .response
        )


class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello World!"

        return (
            handler_input.response_builder.speak(speak_output)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.CancelIntent")(
            handler_input
        ) or ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return handler_input.response_builder.speak(speak_output).response


class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = (
            "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        )
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response


# DynamoDB remember user
class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.persistent_attributes
        if not attr:
            attr["default_stop"] = handler_input.request_envelope.request.intent.slots[
                "stop"
            ].value

        handler_input.attributes_manager.session_attributes = attr

        handler_input.attributes_manager.save_persistent_attributes()
        speak_output = (
            "Welcome back. Your saved stop is {}. You can say Hello or Help?".format(
                attr["default_stop"]
            )
        )
        reprompt = "Say hello or help to start."
        return handler_input.response_builder.speak(speak_output).ask(reprompt).response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder.speak(speak_output)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(BusStopSetterHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(
    IntentReflectorHandler()
)  # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()

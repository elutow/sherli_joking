# slowbro Notes

This document contains notes from reverse-engineering the `slowbro` library.

`slowbro` is a light-weight framework for building speech-based bots. It has an emphasis for supporting bots based on AWS and other Amazon services.

## Some Key Concepts

Many of the concepts seem to be derived from those presented by the Amazon Skills Kit. This section consists of some concepts that are important to understanding how `slowbro` works that may not obvious from a glance.

* All data is stored in JSON format to DynamoDB. To do this, the relevant objects are serialized to/from JSON format using `to_dict()` and `from_dict()` methods.
* When the bot connects with a user, a *session* is created (not unlike what is done for Alexa Skills). A session is a collection of *rounds*, which are defined as a *user turn* and a *bot turn*.
	* A round is started when the user initiates an action, which is either a message or activating the bot; the round ends when the bot submits a response to the user.
	* The data from sessions and rounds are stored as *attributes*. In Labs 1 and 2, round attributes consist of the round index, user message, and bot message.
	* Rounds are indexed by an incrementing integer, starting with `1`.
	* Sessions are identified by a string, which are retrieved from `UserMessage` instances.
	* `slowbro` stores all information about sessions and rounds into DynamoDB.

## Code Structure

* `core` - Core abstractions for constructing bots
	* `bot_base.BotBase` - Abstract base class (ABC) for overall bot logic.
	* `bot_message.BotMessage` - ABC for messages sent from the bot to the user.
	* `bot_builder_base.BotBuilderBase` - ABC for classes that manage instances derived from `BotBase`, known as bot builders. Bot builders seem to follow the [Builder design pattern](https://en.wikipedia.org/wiki/Builder_pattern). Additionally, bot builders are responsible for managing a web server that are used by channels (see below).
	* `dynamodb_utils` - Various functions for interfacing with Amazon DynamoDB
	* `round_saver` - Various abstract and concrete classes for reading and writing rounds to/from DynamoDB.
	* `slowbro_logger` - Logging for the `slowbro` library itself.
	* `user_message` - Classes representing a spoken user message.
		* `UserMessage` - Class representing a message from the user. When it is spoken, it may consist of ASR hypotheses.
* `channels` - Defines channels, which are implementations of the core abstractions for specific bot platforms.
	* `alexaprize` - Channel for the Amazon Skills Kit SDK, presumably used for the requirements of UW's 2017 Alexa Prize AI.
		* `bot_builder.AlexaPrizeBotBuilder` - Implementation of `core.bot_builder_base.BotBuilderBase` using the Alexa Skills Kit SDK.
		* `exception_handlers` - Exception handlers for `ask_sdk_core.skill_builder.SkillBuilder`
		* `request_handlers` - Request handlers for `ask_sdk_core.skill_builder.SkillBuilder`
		* `utils` - Various utilities for converting between Amazon Skill Kit SDK objects and `slowbro` objects.

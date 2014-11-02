# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals

from contextlib import contextmanager
import sys

from mock import Mock, patch
from six.moves import StringIO

from ..plugins.i_result_handler_plugin import IResultHandlerPlugin
from ..plugins.result_handler import QuietTestResultHandler
from ..result import ResultCollecter, TestResult, TestCompletionStatus
from ..testing import unittest


class ExcInfoFixture(object):

    @contextmanager
    def exc_info(self, cls):
        try:
            raise cls()
        except cls:
            yield sys.exc_info()


class TestTextTestResult(ExcInfoFixture, unittest.TestCase):

    def test_result_collector_calls_handlers_start_stop_methods(self):
        # Given
        handler = Mock(spec=IResultHandlerPlugin)
        collector = ResultCollecter()
        collector.add_result_handler(handler)

        # When
        handler.reset_mock()
        collector.startTestRun()

        # Then
        handler.start_test_run.assert_called_once_with()
        self.assertFalse(handler.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.start_test.called)
        self.assertFalse(handler.stop_test.called)

        # When
        handler.reset_mock()
        collector.stopTestRun()

        # Then
        handler.stop_test_run.assert_called_once_with()
        self.assertFalse(handler.called)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.start_test.called)
        self.assertFalse(handler.stop_test.called)

        # When
        handler.reset_mock()
        collector.startTest(self)

        # Then
        handler.start_test.assert_called_once_with(self)
        self.assertFalse(handler.called)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.stop_test.called)

        # When
        handler.reset_mock()
        collector.stopTest(self)

        # Then
        handler.stop_test.assert_called_once_with(self)
        self.assertFalse(handler.called)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.start_test.called)

    def test_result_collector_calls_handlers_on_error(self):
        # Given
        handler = Mock(spec=IResultHandlerPlugin)
        collector = ResultCollecter()
        collector.add_result_handler(handler)

        # When
        with self.exc_info(RuntimeError) as exc_info:
            # Given
            expected_result = TestResult.from_test_case(
                self, TestCompletionStatus.error, exception=exc_info)
            collector.addError(self, exc_info)

        # Then
        handler.assert_called_once_with(expected_result)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.start_test.called)
        self.assertFalse(handler.stop_test.called)
        self.assertFalse(collector.wasSuccessful())

    def test_result_collector_calls_handlers_on_failure(self):
        # Given
        handler = Mock(spec=IResultHandlerPlugin)
        collector = ResultCollecter()
        collector.add_result_handler(handler)

        # When
        with self.exc_info(AssertionError) as exc_info:
            # Given
            expected_result = TestResult.from_test_case(
                self, TestCompletionStatus.failure, exception=exc_info)
            collector.addFailure(self, exc_info)

        # Then
        handler.assert_called_once_with(expected_result)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.start_test.called)
        self.assertFalse(handler.stop_test.called)
        self.assertFalse(collector.wasSuccessful())

    def test_result_collector_calls_handlers_on_success(self):
        # Given
        handler = Mock(spec=IResultHandlerPlugin)
        collector = ResultCollecter()
        collector.add_result_handler(handler)

        # When
        expected_result = TestResult.from_test_case(
            self, TestCompletionStatus.success)
        collector.addSuccess(self)

        # Then
        handler.assert_called_once_with(expected_result)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.start_test.called)
        self.assertFalse(handler.stop_test.called)
        self.assertTrue(collector.wasSuccessful())

    def test_result_collector_calls_handlers_on_skip(self):
        # Given
        handler = Mock(spec=IResultHandlerPlugin)
        collector = ResultCollecter()
        collector.add_result_handler(handler)

        # When
        expected_result = TestResult.from_test_case(
            self, TestCompletionStatus.skipped, message='reason')
        collector.addSkip(self, 'reason')

        # Then
        handler.assert_called_once_with(expected_result)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.start_test.called)
        self.assertFalse(handler.stop_test.called)
        self.assertTrue(collector.wasSuccessful())

    def test_result_collector_calls_handlers_on_expected_fail(self):
        # Given
        handler = Mock(spec=IResultHandlerPlugin)
        collector = ResultCollecter()
        collector.add_result_handler(handler)

        # When
        with self.exc_info(RuntimeError) as exc_info:
            # Given
            expected_result = TestResult.from_test_case(
                self, TestCompletionStatus.expected_failure,
                exception=exc_info)
            collector.addExpectedFailure(self, exc_info)

        # Then
        handler.assert_called_once_with(expected_result)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.start_test.called)
        self.assertFalse(handler.stop_test.called)
        self.assertTrue(collector.wasSuccessful())

    def test_result_collector_calls_handlers_on_unexpected_success(self):
        # Given
        handler = Mock(spec=IResultHandlerPlugin)
        collector = ResultCollecter()
        collector.add_result_handler(handler)

        # When
        expected_result = TestResult.from_test_case(
            self, TestCompletionStatus.unexpected_success)
        collector.addUnexpectedSuccess(self)

        # Then
        handler.assert_called_once_with(expected_result)
        self.assertFalse(handler.start_test_run.called)
        self.assertFalse(handler.stop_test_run.called)
        self.assertFalse(handler.start_test.called)
        self.assertFalse(handler.stop_test.called)
        self.assertFalse(collector.wasSuccessful())

    def test_result_collector_should_stop(self):
        # Given
        collector = ResultCollecter()

        # Then
        self.assertFalse(collector.shouldStop)

        # When
        collector.stop()

        # Then
        self.assertTrue(collector.shouldStop)


class TestQuietResultHandler(ExcInfoFixture, unittest.TestCase):

    @patch('sys.stderr', new_callable=StringIO)
    def test_no_output_start_test_run(self, stderr):
        # Given
        handler = QuietTestResultHandler(test_count=1)

        # When
        handler.start_test_run()

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '')

    @patch('sys.stderr', new_callable=StringIO)
    def test_no_output_stop_test_run(self, stderr):
        # Given
        handler = QuietTestResultHandler(test_count=1)

        # When
        handler.stop_test_run()

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '\n')

    @patch('sys.stderr', new_callable=StringIO)
    def test_no_output_start_test(self, stderr):
        # Given
        handler = QuietTestResultHandler(test_count=1)

        # When
        handler.start_test(self)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '')

    @patch('sys.stderr', new_callable=StringIO)
    def test_no_output_stop_test(self, stderr):
        # Given
        handler = QuietTestResultHandler(test_count=1)

        # When
        handler.stop_test(self)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '')

    @patch('sys.stderr', new_callable=StringIO)
    def test_no_output_on_error(self, stderr):
        # Given
        handler = QuietTestResultHandler(test_count=1)
        with self.exc_info(RuntimeError) as exc_info:
            result = TestResult.from_test_case(
                self, TestCompletionStatus.error, exception=exc_info)

        # When
        handler(result)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '')

    @patch('sys.stderr', new_callable=StringIO)
    def test_no_output_on_failure(self, stderr):
        # Given
        handler = QuietTestResultHandler(test_count=1)
        with self.exc_info(AssertionError) as exc_info:
            result = TestResult.from_test_case(
                self, TestCompletionStatus.failure, exception=exc_info)

        # When
        handler(result)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '')

    @patch('sys.stderr', new_callable=StringIO)
    def test_no_output_on_success(self, stderr):
        # Given
        handler = QuietTestResultHandler(test_count=1)
        result = TestResult.from_test_case(
            self, TestCompletionStatus.success)

        # When
        handler(result)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '')

    @patch('sys.stderr', new_callable=StringIO)
    def test_no_output_on_skip(self, stderr):
        # Given
        handler = QuietTestResultHandler(test_count=1)
        result = TestResult.from_test_case(
            self, TestCompletionStatus.skipped, message='reason')

        # When
        handler(result)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '')

    @patch('sys.stderr', new_callable=StringIO)
    def test_no_output_on_expected_fail(self, stderr):
        # Given
        handler = QuietTestResultHandler(test_count=1)
        with self.exc_info(RuntimeError) as exc_info:
            result = TestResult.from_test_case(
                self, TestCompletionStatus.expected_failure,
                exception=exc_info)

        # When
        handler(result)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '')

    @patch('sys.stderr', new_callable=StringIO)
    def test_no_output_on_unexpected_success(self, stderr):
        # Given
        handler = QuietTestResultHandler(test_count=1)
        result = TestResult.from_test_case(
            self, TestCompletionStatus.unexpected_success)

        # When
        handler(result)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '')

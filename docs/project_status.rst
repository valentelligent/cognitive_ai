Project Status and Changes
========================

Last Updated: 2024-12-12 10:07:26

Core Components
---------------

**core/__init__.py**


Functions:
* ``initialize_system``
* ``initialize_adaptive_system``
* ``initialize_cognitive_system``
* ``initialize_data_system``

Last Modified: 2024-12-11T23:40:18.710879

**core/adaptive/interface_manager.py**

Classes:
* ``UserBehaviorMetrics``
* ``AdaptiveInterfaceManager``

Functions:
* ``__init__``
* ``analyze_user_behavior``
* ``adapt_interface``
* ``_compute_optimal_layout``
* ``_adjust_complexity``
* ``_determine_support_level``

Last Modified: 2024-12-12T00:39:11.095851

**core/gpu/cuda_operations.py**

Classes:
* ``GPUManager``

Functions:
* ``__init__``
* ``_initialize_gpu``
* ``get_memory_info``
* ``accelerate_cognitive_load``
* ``_gpu_cognitive_load``
* ``_cpu_cognitive_load``
* ``__del__``

Last Modified: 2024-12-12T06:44:05.478370

**core/monitoring/cognitive_tracker.py**

Classes:
* ``CognitiveInteractionTracker``

Functions:
* ``__init__``
* ``_analyze_memory_patterns``
* ``_analyze_executive_function``
* ``_analyze_language_patterns``
* ``_analyze_perception_action``
* ``_analyze_usage_patterns``
* ``_detect_behavioral_changes``
* ``_calculate_cognitive_load``
* ``start_task``
* ``stop_task``
* ``_calculate_typing_speed``
* ``_calculate_error_rate``
* ``_calculate_focus_score``
* ``_handle_keyboard_event``
* ``_handle_window_change``
* ``_log_event``
* ``_gpu_cognitive_load``
* ``_initialize_cuda``

Last Modified: 2024-12-12T10:07:26

**core/monitoring/gpu_monitor.py**

Classes:
* ``GPUStats``
* ``GPUMonitor``

Functions:
* ``__init__``
* ``_initialize_gpu``
* ``get_gpu_stats``
* ``start_monitoring``
* ``monitor_loop``
* ``stop_monitoring``
* ``get_memory_usage``
* ``get_performance_metrics``
* ``__del__``

Last Modified: 2024-12-12T07:16:01.199146

**core/monitoring/interaction_tracker.py**

Classes:
* ``InteractionTracker``

Functions:
* ``__init__``
* ``_setup_log_file``
* ``_setup_keyboard_hooks``
* ``_setup_mouse_hooks``
* ``_get_active_window_info``
* ``_get_system_metrics``
* ``_handle_keyboard_event``
* ``_handle_mouse_event``
* ``_get_active_window``
* ``_log_event``
* ``_flush_events``
* ``start``
* ``stop``
* ``get_current_stats``

Last Modified: 2024-12-12T04:49:16.255904

**core/monitoring/__init__.py**


Last Modified: 2024-12-11T23:59:19.780007

Test Suite
----------

**tests/conftest.py**


Last Modified: 2024-12-12T04:02:46.235155

**tests/test_cognitive_metrics.py**

Test Classes:
* ``TestCognitiveMetrics``

Last Modified: 2024-12-12T03:56:14.408046

**tests/test_cognitive_tracker.py**

Test Classes:
* ``TestCognitiveInteractionTracker``

Last Modified: 2024-12-12T04:15:30.940577

**tests/test_cuda_operations.py**

Test Classes:
* ``TestGPUManager``

Last Modified: 2024-12-12T06:44:18.634616

**tests/test_gpu_monitor.py**

Test Classes:
* ``TestGPUMonitor``

Last Modified: 2024-12-12T07:16:34.710410

**tests/test_interaction_tracker.py**

Test Classes:
* ``TestInteractionTracker``

Last Modified: 2024-12-12T04:49:28.043287

**tests/__init__.py**


Last Modified: 2024-12-12T03:47:36.797194

Configuration
-------------

**pyproject.toml**
Last Modified: 2024-12-12T07:13:32.859612

**setup.py**
Last Modified: 2024-12-12T07:13:38.032500

**requirements.txt**
Last Modified: 2024-12-12T07:13:22.432741

**environment.yml**
Last Modified: 2024-12-12T07:01:22.182082

**.pre-commit-config.yaml**
Last Modified: 2024-12-12T07:02:37.512247

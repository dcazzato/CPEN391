# TCL File Generated by Component Editor 15.0
# Mon Feb 12 15:42:28 PST 2018
# DO NOT MODIFY


# 
# graphic_controller "graphic_controller" v1.0
#  2018.02.12.15:42:28
# 
# 

# 
# request TCL package from ACDS 15.0
# 
package require -exact qsys 15.0


# 
# module graphic_controller
# 
set_module_property DESCRIPTION ""
set_module_property NAME graphic_controller
set_module_property VERSION 1.0
set_module_property INTERNAL false
set_module_property OPAQUE_ADDRESS_MAP true
set_module_property AUTHOR ""
set_module_property DISPLAY_NAME graphic_controller
set_module_property INSTANTIATE_IN_SYSTEM_MODULE true
set_module_property EDITABLE true
set_module_property REPORT_TO_TALKBACK false
set_module_property ALLOW_GREYBOX_GENERATION false
set_module_property REPORT_HIERARCHY false


# 
# file sets
# 
add_fileset QUARTUS_SYNTH QUARTUS_SYNTH "" ""
set_fileset_property QUARTUS_SYNTH TOP_LEVEL signal_control
set_fileset_property QUARTUS_SYNTH ENABLE_RELATIVE_INCLUDE_PATHS false
set_fileset_property QUARTUS_SYNTH ENABLE_FILE_OVERWRITE_MODE false
add_fileset_file signal_control.sv SYSTEM_VERILOG PATH signal_control.sv TOP_LEVEL_FILE


# 
# parameters
# 
add_parameter idle STD_LOGIC_VECTOR 0
set_parameter_property idle DEFAULT_VALUE 0
set_parameter_property idle DISPLAY_NAME idle
set_parameter_property idle TYPE STD_LOGIC_VECTOR
set_parameter_property idle UNITS None
set_parameter_property idle ALLOWED_RANGES 0:31
set_parameter_property idle HDL_PARAMETER true
add_parameter getVal STD_LOGIC_VECTOR 5
set_parameter_property getVal DEFAULT_VALUE 5
set_parameter_property getVal DISPLAY_NAME getVal
set_parameter_property getVal TYPE STD_LOGIC_VECTOR
set_parameter_property getVal UNITS None
set_parameter_property getVal ALLOWED_RANGES 0:31
set_parameter_property getVal HDL_PARAMETER true
add_parameter writeVal STD_LOGIC_VECTOR 3
set_parameter_property writeVal DEFAULT_VALUE 3
set_parameter_property writeVal DISPLAY_NAME writeVal
set_parameter_property writeVal TYPE STD_LOGIC_VECTOR
set_parameter_property writeVal UNITS None
set_parameter_property writeVal ALLOWED_RANGES 0:31
set_parameter_property writeVal HDL_PARAMETER true


# 
# display items
# 


# 
# connection point clock
# 
add_interface clock clock end
set_interface_property clock clockRate 0
set_interface_property clock ENABLED true
set_interface_property clock EXPORT_OF ""
set_interface_property clock PORT_NAME_MAP ""
set_interface_property clock CMSIS_SVD_VARIABLES ""
set_interface_property clock SVD_ADDRESS_GROUP ""

add_interface_port clock clk clk Input 1


# 
# connection point reset
# 
add_interface reset reset end
set_interface_property reset associatedClock clock
set_interface_property reset synchronousEdges DEASSERT
set_interface_property reset ENABLED true
set_interface_property reset EXPORT_OF ""
set_interface_property reset PORT_NAME_MAP ""
set_interface_property reset CMSIS_SVD_VARIABLES ""
set_interface_property reset SVD_ADDRESS_GROUP ""

add_interface_port reset reset reset Input 1


# 
# connection point slave
# 
add_interface slave avalon end
set_interface_property slave addressUnits WORDS
set_interface_property slave associatedClock clock
set_interface_property slave associatedReset reset
set_interface_property slave bitsPerSymbol 8
set_interface_property slave burstOnBurstBoundariesOnly false
set_interface_property slave burstcountUnits WORDS
set_interface_property slave explicitAddressSpan 0
set_interface_property slave holdTime 0
set_interface_property slave linewrapBursts false
set_interface_property slave maximumPendingReadTransactions 0
set_interface_property slave maximumPendingWriteTransactions 0
set_interface_property slave readLatency 0
set_interface_property slave readWaitTime 1
set_interface_property slave setupTime 0
set_interface_property slave timingUnits Cycles
set_interface_property slave writeWaitTime 0
set_interface_property slave ENABLED true
set_interface_property slave EXPORT_OF ""
set_interface_property slave PORT_NAME_MAP ""
set_interface_property slave CMSIS_SVD_VARIABLES ""
set_interface_property slave SVD_ADDRESS_GROUP ""

add_interface_port slave write_slave write Input 1
add_interface_port slave address address Input 16
add_interface_port slave data_in writedata Input 32
set_interface_assignment slave embeddedsw.configuration.isFlash 0
set_interface_assignment slave embeddedsw.configuration.isMemoryDevice 0
set_interface_assignment slave embeddedsw.configuration.isNonVolatileStorage 0
set_interface_assignment slave embeddedsw.configuration.isPrintableDevice 0


# 
# connection point avalon_master
# 
add_interface avalon_master avalon start
set_interface_property avalon_master addressUnits SYMBOLS
set_interface_property avalon_master associatedClock clock
set_interface_property avalon_master associatedReset reset
set_interface_property avalon_master bitsPerSymbol 8
set_interface_property avalon_master burstOnBurstBoundariesOnly false
set_interface_property avalon_master burstcountUnits WORDS
set_interface_property avalon_master doStreamReads false
set_interface_property avalon_master doStreamWrites false
set_interface_property avalon_master holdTime 0
set_interface_property avalon_master linewrapBursts false
set_interface_property avalon_master maximumPendingReadTransactions 0
set_interface_property avalon_master maximumPendingWriteTransactions 0
set_interface_property avalon_master readLatency 0
set_interface_property avalon_master readWaitTime 1
set_interface_property avalon_master setupTime 0
set_interface_property avalon_master timingUnits Cycles
set_interface_property avalon_master writeWaitTime 0
set_interface_property avalon_master ENABLED true
set_interface_property avalon_master EXPORT_OF ""
set_interface_property avalon_master PORT_NAME_MAP ""
set_interface_property avalon_master CMSIS_SVD_VARIABLES ""
set_interface_property avalon_master SVD_ADDRESS_GROUP ""

add_interface_port avalon_master write_master write Output 1
add_interface_port avalon_master wait_request waitrequest Input 1
add_interface_port avalon_master byteenable byteenable Output 4
add_interface_port avalon_master data_out writedata Output 32
add_interface_port avalon_master address_out address Output 16

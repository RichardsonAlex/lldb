//===-- RegisterContextPOSIX_mips64.h ---------------------------*- C++ -*-===//
//
//                     The LLVM Compiler Infrastructure
//
// This file is distributed under the University of Illinois Open Source
// License. See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//

#ifndef liblldb_RegisterContextPOSIX_mips64_H_
#define liblldb_RegisterContextPOSIX_mips64_H_

#include "lldb/Core/Log.h"
#include "RegisterContextPOSIX.h"
#include "RegisterContext_mips64.h"

class ProcessMonitor;

// ---------------------------------------------------------------------------
// Internal codes for all mips64 registers.
// ---------------------------------------------------------------------------
enum
{
    k_first_gpr_mips64,
    gpr_zero_mips64 = k_first_gpr_mips64,
    gpr_r1_mips64,
    gpr_r2_mips64,
    gpr_r3_mips64,
    gpr_r4_mips64,
    gpr_r5_mips64,
    gpr_r6_mips64,
    gpr_r7_mips64,
    gpr_r8_mips64,
    gpr_r9_mips64,
    gpr_r10_mips64,
    gpr_r11_mips64,
    gpr_r12_mips64,
    gpr_r13_mips64,
    gpr_r14_mips64,
    gpr_r15_mips64,
    gpr_r16_mips64,
    gpr_r17_mips64,
    gpr_r18_mips64,
    gpr_r19_mips64,
    gpr_r20_mips64,
    gpr_r21_mips64,
    gpr_r22_mips64,
    gpr_r23_mips64,
    gpr_r24_mips64,
    gpr_r25_mips64,
    gpr_r26_mips64,
    gpr_r27_mips64,
    gpr_gp_mips64,
    gpr_sp_mips64,
    gpr_r30_mips64,
    gpr_ra_mips64,
    gpr_sr_mips64,
    gpr_mullo_mips64,
    gpr_mulhi_mips64,
    gpr_badvaddr_mips64,
    gpr_cause_mips64,
    gpr_pc_mips64,
    gpr_ic_mips64,
    gpr_dummy_mips64,
    k_last_gpr_mips64 = gpr_dummy_mips64,

    /* CHERI capability registers */
    cap_c0_mips64,
    k_first_cr_mips64 = cap_c0_mips64,
    cap_c1_mips64,
    cap_c2_mips64,
    cap_c3_mips64,
    cap_c4_mips64,
    cap_c5_mips64,
    cap_c6_mips64,
    cap_c7_mips64,
    cap_c8_mips64,
    cap_c9_mips64,
    cap_c10_mips64,
    cap_c11_mips64,
    cap_c12_mips64,
    cap_c13_mips64,
    cap_c14_mips64,
    cap_c15_mips64,
    cap_c16_mips64,
    cap_c17_mips64,
    cap_c18_mips64,
    cap_c19_mips64,
    cap_c20_mips64,
    cap_c21_mips64,
    cap_c22_mips64,
    cap_c23_mips64,
    cap_c24_mips64,
    cap_c25_mips64,
    cap_c26_mips64,
    cap_c27_mips64,
    cap_c28_mips64,
    cap_c29_mips64,
    cap_c30_mips64,
    cap_c31_mips64,
    k_last_cr_mips64 = cap_c31_mips64,

    k_num_gpr_registers_mips64 = k_last_gpr_mips64 - k_first_gpr_mips64 + 1,
    k_num_cr_registers_mips64 = k_last_cr_mips64 - k_first_cr_mips64 + 1,
    k_num_registers_mips64 = k_num_gpr_registers_mips64 + k_num_cr_registers_mips64
};

class RegisterContextPOSIX_mips64
  : public lldb_private::RegisterContext
{
public:
    RegisterContextPOSIX_mips64 (lldb_private::Thread &thread,
                            uint32_t concrete_frame_idx,
                            lldb_private::RegisterInfoInterface *register_info);

    ~RegisterContextPOSIX_mips64();

    void
    Invalidate();

    void
    InvalidateAllRegisters();

    size_t
    GetRegisterCount();

    virtual size_t
    GetGPRSize();

    virtual unsigned
    GetRegisterSize(unsigned reg);

    virtual unsigned
    GetRegisterOffset(unsigned reg);

    const lldb_private::RegisterInfo *
    GetRegisterInfoAtIndex(size_t reg);

    size_t
    GetRegisterSetCount();

    const lldb_private::RegisterSet *
    GetRegisterSet(size_t set);

    const char *
    GetRegisterName(unsigned reg);

    uint32_t
    ConvertRegisterKindToRegisterNumber(lldb::RegisterKind kind, uint32_t num);

protected:
    uint64_t m_gpr_mips64[k_num_gpr_registers_mips64];         // general purpose registers.
    std::unique_ptr<lldb_private::RegisterInfoInterface> m_register_info_ap; // Register Info Interface (FreeBSD or Linux)

    // Determines if an extended register set is supported on the processor running the inferior process.
    virtual bool
    IsRegisterSetAvailable(size_t set_index);

    virtual const lldb_private::RegisterInfo *
    GetRegisterInfo();

    bool
    IsGPR(unsigned reg);

    bool
    IsFPR(unsigned reg);

    lldb::ByteOrder GetByteOrder();

    virtual bool ReadGPR() = 0;
    virtual bool ReadFPR() = 0;
    virtual bool WriteGPR() = 0;
    virtual bool WriteFPR() = 0;
};

#endif // #ifndef liblldb_RegisterContextPOSIX_mips64_H_

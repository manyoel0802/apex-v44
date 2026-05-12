# --- 🛡️ TOOLS (AUDIT & PORTFOLIO) ---
st.divider()
ca, cb = st.columns(2)

with ca:
    st.subheader("🔍 All-Cap Tactical Audit")
    tid_input = st.text_input("Ticker Target (Contoh: DFAM):", key="audit_input").upper()
    if st.button("🚀 Run Tactical Audit"):
        if tid_input:
            with st.spinner(f"Interogasi {tid_input}..."):
                # Menghilangkan .JK jika user terbiasa mengetiknya
                clean_ticker = tid_input.replace(".JK", "")
                res, p_val = run_deep_audit(clean_ticker, ihsg_ret)
                
                if res:
                    st.write(f"### Vonis {tid_input}:")
                    for k, v in res.items():
                        st.markdown(f"<span class='{'audit-pass' if v else 'audit-fail'}'>{'✅' if v else '❌'} {k}</span>", unsafe_allow_html=True)
                    
                    if all(res.values()): 
                        st.success("WORLD CHAMPION CONFIRMED 🚀")
                    
                    st.markdown(f"""
                    <div class='pyramid-panel'>
                        <b>📐 Strategic Plan:</b><br>
                        Entry: {int(p_val)} | Next: {int(p_val*1.05)} | SL: {int(p_val*(1-risk/100))}
                    </div>
                    """, unsafe_allow_html=True)
                else: 
                    st.error("Data GoAPI tidak ditemukan untuk ticker ini. Pastikan ticker terdaftar di IDX.")

with cb:
    st.subheader("🛡️ Portfolio & Buy Manager")
    st.write(f"Market Health: **{mkt_breadth}%**")
    pid = st.text_input("Add to Portfolio/Trade:", key="port_input").upper()
    if st.button("🛒 EKSEKUSI"): 
        if pid:
            st.success(f"Signal {pid} berhasil dikirim ke Command Center!")
        else:
            st.warning("Masukkan kode saham terlebih dahulu.")

st.caption(f"V53.0 PRO-CONNECT | Powered by GoAPI | Last Heartbeat: {now.strftime('%H:%M:%S')} WIB")
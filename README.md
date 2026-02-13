gen-signedexchange \
  -mode cert \
  -certificate cert.crt \
  -privateKey cert.key \
  -uri https://124.16.75.162:31053 \
  -output cert.cbor

go run go/signedexchange/cmd/gen-signedexchange/main.go \
  -uri https://124.16.75.162:31053/ \
  -content exp.html \
  -certificate cert.crt \
  -privateKey cert.key \
  -certUrl http://admin.yyhs.club:31024/cert.cbor \
  -validityUrl https://124.16.75.162:31053/resource.validity.msg \
  -date 2026-02-12T00:00:00Z \
  -expire 168h \
  -o exp.sxg

go run go/signedexchange/cmd/gen-signedexchange/main.go \
  -uri https://124.16.75.162:31053/ \
  -content exp.html \
  -certificate cert.crt \
  -privateKey cert.key \
  -certUrl "$DATA_URI" \
  -validityUrl https://124.16.75.162:31053/resource.validity.msg \
  -date 2026-02-12T00:00:00Z \
  -expire 168h \
  -o exp.sxg